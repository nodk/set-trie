import logging
import pytest
from set_trie import SetTrie

logger = logging.getLogger(name=__name__)


@pytest.fixture
def set_trie_ins():
    return SetTrie[str]()


def test_word_str(set_trie_ins):
    test_word = set_trie_ins.create_word(["a", "b", "c"])

    # Call twice for idempotency check.
    assert str(test_word) == "a,b,c"
    assert str(test_word) == "a,b,c"


def test_set_trie_insert(set_trie_ins):
    abd = set_trie_ins.create_word(["a", "b", "d"])
    abe = set_trie_ins.create_word(["a", "b", "e"])

    set_trie_ins.insert(abe)
    set_trie_ins.insert(abd)

    sts = set_trie_ins.to_str()
    assert sts == "".join([" Root  a  b [d]", "\n",
                           "            [e]"])

    set_trie_ins.insert(set_trie_ins.create_word(["a", "b"]))

    sts = set_trie_ins.to_str()
    assert sts == "".join([" Root  a [b][d]", "\n",
                           "            [e]"])

    set_trie_ins.insert(set_trie_ins.create_word(["a", "b", "d", "e"]))

    sts = set_trie_ins.to_str()
    assert sts == "".join([" Root  a [b][d][e]", "\n",
                           "            [e]"])

    set_trie_ins.insert(set_trie_ins.create_word(["a", "b", "c"]))

    sts = set_trie_ins.to_str()
    assert sts == "".join([" Root  a [b][c]", "\n",
                           "            [d][e]", "\n",
                           "            [e]"])

    set_trie_ins.insert(set_trie_ins.create_word(["a", "b", "d", "f"]))

    sts = set_trie_ins.to_str()
    assert sts == "".join([" Root  a [b][c]", "\n",
                           "            [d][e]", "\n",
                           "               [f]", "\n",
                           "            [e]"])


def test_set_trie_search(set_trie_ins):
    abc = set_trie_ins.create_word(["a", "b", "c"])
    assert set_trie_ins.search(abc) is False
    set_trie_ins.insert(set_trie_ins.create_word(["a", "b", "c", "d"]))
    set_trie_ins.insert(set_trie_ins.create_word(["a", "b"]))
    assert set_trie_ins.search(abc) is False
    set_trie_ins.insert(abc)
    assert set_trie_ins.search(abc) is True
