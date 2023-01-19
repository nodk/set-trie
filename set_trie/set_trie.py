# -*- coding: utf-8 -*-
"""Implementation of a set-trie algorithm.

Original paper:
Iztok Savnik.
Index Data Structure for Fast Subset and Superset Queries.
1st Cross-Domain Conference and Workshop on Availability,
Reliability, and Security in Information Systems (CD-ARES),
Sep 2013, Regensburg, Germany. pp.134-148. ⟨hal-01506780⟩
https://hal.inria.fr/hal-01506780
"""

# import collections
from typing import TypeVar, Generic, Iterator, List, Iterable
from itertools import tee
from bisect import bisect_left
import logging
from ordered_set import OrderedSet

_logger = logging.getLogger(name=__name__)

T = TypeVar("T")
V = TypeVar("V")

def _first_true(iterable: Iterable[T], default=False, pred=None) -> T:
    """Returns the first true value in the iterable.

    If no true value is found, returns *default*

    If *pred* is not None, returns the first item
    for which pred(item) is true.

    Copied from official python docs.
    https://docs.python.org/ja/3/library/itertools.html
    """
    return next(filter(pred, iterable), default)


class _Word(Generic[T]):
    orig_itr: Iterator[OrderedSet[T]]
    itr: Iterator[OrderedSet[T]]

    def __init__(self, itr: Iterable[OrderedSet[T]]):
        # oset = OrderedSet(value)
        self.orig_itr, self.itr = tee(itr, 2)

    @classmethod
    def from_value(cls, value: OrderedSet[T]):
        """
        Create Word instance from OrderedSet instance.
        """
        return cls(iter(value))

    @classmethod
    # def copy(cls, word: T_Word[T]):
    def copy(cls, word):
        """
        Copy Word instance.
        """
        dup, word.itr = tee(word.itr, 2)
        return cls(dup)

    def current_element(self) -> T:
        """
        Return current element of Word, corresponds to
        word.currentElement and word.existsCurrentElement in original paper.
        """
        return next(self.itr, None)

    def __str__(self) -> str:
        tmp, self.itr = tee(self.itr, 2)
        strlist = list(map(str, tmp))
        return ",".join(strlist)

    def goto_first_element(self):
        """
        Reset iterator position to first element.
        word.gotoFirstElement in original paper.
        """
        self.orig_itr, self.itr = tee(self.orig_itr, 2)


class _Node(Generic[T, V]):
    label: T
    is_last: bool = False

    def __init__(self, label):
        self.label = label
        self.children: List[_Node] = []

    def _find_children(self, label):
        return _first_true(self.children, None, lambda _n: _n.label == label)

    def insert(self, word: _Word[T]) -> None:
        """
        if (word.existsCurrentElement) then
            if (exists child of node labeled word.currentElement) then
                nextNode = child of node labeled word.currentElement;
            else
                nextNode = create child of node labeled word.currentElement;
            end if
            insert(nextNode, word.gotoNextElement)
        else
            node’s flag_last = true;
        end if
        """

        w_ce = word.current_element()
        if w_ce is not None:
            next_node = self._find_children(w_ce)
            if next_node is None:
                next_node = _Node(w_ce)
                cmap = list(map(lambda n: n.label, self.children))
                idx = bisect_left(cmap, next_node.label)
                self.children = self.children[:idx] + \
                    [next_node] + self.children[idx:]
            next_node.insert(word)
        else:
            self.is_last = True

    def search(self, word: _Word[T]) -> bool:
        """
        if (word.existsCurrentElement) then
            if (there exists child of node labeled word.currentElement) then
                matchNode = child vertex of node labeled word.currentElement;
                search(matchNode, word.gotoNextElement);
            else
                return false;
            end if
        else
            return (node’s last_flag == true) ;
        end if
        """
        w_ce = word.current_element()
        _logger.debug(w_ce)
        if w_ce is not None:
            match_node = self._find_children(w_ce)
            if match_node is None:
                return False
            return match_node.search(word)
        else:
            return self.is_last

    def __str__(self) -> str:
        return self._to_str("", "")

    def _to_str(self, offset_str1, offset_str2):
        if self.is_last:
            value_str = "[{}]".format(self.label)
        else:
            value_str = " {} ".format(self.label)

        psuedo_str = " " * len(value_str)

        if len(self.children) == 0:
            return offset_str1 + value_str
        else:
            lst = []
            lst.append(self.children[0]._to_str(
                offset_str1+value_str, offset_str2+psuedo_str))
            for i in range(1, len(self.children)):
                if self.label == self.children[i].label:
                    continue
                lst.append(self.children[i]._to_str(
                    offset_str2+psuedo_str, offset_str2+psuedo_str))
            ret = "\n".join(lst)
            return ret


def _exists_subset(node: _Node[T, V], word: _Word[T]) -> bool:
    """
    if (node.last_flag == true) then
        return true;
    end if
    if (not word.existsCurrentElement) then
        return false;
    end if
    found = false;
    if (node has child labeled word.currentElement) then
        nextNode = child of node labeled word.currentElement;
        found = existsSubset(nextNode, word.gotoNextElement);
    end if
    if (!found) then
        return existsSubset(node,word.gotoNextElement);
    else
        return true;
    end if
    """
    if node.is_last:
        return True
    w_ce = word.current_element()
    if w_ce is None:
        return False
    found = False
    next_node = node._find_children(w_ce)
    if next_node is not None:
        # use copied iterator for
        found = _exists_subset(next_node, _Word.copy(word))
    if not found:
        return _exists_subset(node, word)
    else:
        return True


def _exists_superset(node: _Node[T, V], word: _Word[T]):
    """
    if (not word.existsCurrentElement) then
        return true;
    end if
    found = false;
    from = word.currentElement;
    upto = word.nextElement if it exists and N otherwise;
    for (each child of node labeled l: from < l ≤ upto) & (while not found) do
        if (child is labeled upto) then
            found = existsSuperset(child,word.gotoNextElement);
        else
            found = existsSuperset(child,word);
        end if
    end for
    """
    _w0 = word.copy(word)
    lb = word.current_element()
    _w1 = word.copy(word)
    if lb is None:
        return False
    found = False
    ub = word.current_element()
    itr:Iterable[_Node] = filter(lambda c:c > lb, node.children)
    while not found:
        child = next(itr, None)
        if child is None or child.label > ub:
            break
        if child.label == ub:
            found = _exists_superset(child,_w1)
        else:
            found = _exists_superset(child,_w0)
    return found


class SetTrie(Generic[T]):
    """_summary_

    Args:
        Generic (_type_): _description_
    """
    def __init__(self):
        self.root_node = _Node("Root")

    def insert(self, word: _Word[T]):
        """_summary_

        Args:
            word (_Word[T]): _description_
        """
        _w = word.copy(word)
        self.root_node.insert(_w)

    def search(self, word: _Word[T]):
        """_summary_

        Args:
            word (_Word[T]): _description_

        Returns:
            _type_: _description_
        """
        _w = word.copy(word)
        return self.root_node.search(_w)

    def exists_subset(self, word):
        """_summary_

        Args:
            word (_type_): _description_

        Returns:
            _type_: _description_
        """
        _w = word.copy(word)
        return _exists_subset(self.root_node, _w)

    def exists_superset(self, word):
        """_summary_

        Args:
            word (_type_): _description_

        Returns:
            _type_: _description_
        """
        _w = word.copy(word)
        return _exists_superset(self.root_node, _w)

    def create_word(self, content: List[T]):
        """_summary_

        Args:
            content (List[T]): _description_

        Returns:
            _type_: _description_
        """
        return _Word.from_value(OrderedSet(sorted(content)))

    def to_str(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return str(self.root_node)
