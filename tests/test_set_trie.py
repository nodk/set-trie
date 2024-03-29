import logging
import pytest
from set_trie import SetTrie

logger = logging.getLogger(name=__name__)


@pytest.fixture
def set_trie_ins():
    return SetTrie[str]()


def test_word_str(set_trie_ins: SetTrie[str]):
    test_word = set_trie_ins.create_word(["a", "b", "c"])

    # Call twice for idempotency check.
    assert str(test_word) == "a,b,c"
    assert str(test_word) == "a,b,c"


def test_set_trie_insert(set_trie_ins: SetTrie[str]):
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


def test_set_trie_search(set_trie_ins: SetTrie[str]):
    logger.debug(set_trie_ins.to_str())
    abc = set_trie_ins.create_word(["a", "b", "c"])
    assert set_trie_ins.search(abc) is False
    
    set_trie_ins.insert(set_trie_ins.create_word(["a", "b", "c", "d"]))
    set_trie_ins.insert(set_trie_ins.create_word(["a", "b"]))
    logger.debug(set_trie_ins.to_str())
    assert set_trie_ins.search(abc) is False
    
    set_trie_ins.insert(set_trie_ins.create_word(["a", "b", "c", "e", "f"]))
    logger.debug(set_trie_ins.to_str())
    assert set_trie_ins.search(abc) is False

    set_trie_ins.insert(set_trie_ins.create_word(["a", "b", "c"]))
    logger.debug(set_trie_ins.to_str())
    assert set_trie_ins.search(abc) is True

class TestSetTrieExistsSubset:
    def test_set_trie_exists_subset_1(self, set_trie_ins: SetTrie[str]):
        abc = set_trie_ins.create_word(["a", "b", "c"])
        set_trie_ins.insert(set_trie_ins.create_word(["a", "b", "c", "d"]))
        set_trie_ins.insert(set_trie_ins.create_word(["a", "b", "e", "f"]))
        assert set_trie_ins.exists_subset(abc) is False
        
        set_trie_ins.insert(set_trie_ins.create_word(["a", "b"]))
        assert set_trie_ins.exists_subset(abc) is True
    
    def test_set_trie_exists_subset_2(self, set_trie_ins: SetTrie[str]):
        abc = set_trie_ins.create_word(["a", "b", "c"])
        set_trie_ins.insert(set_trie_ins.create_word(["b", "d"]))
        assert set_trie_ins.exists_subset(abc) is False
    
        set_trie_ins.insert(set_trie_ins.create_word(["d"]))
        assert set_trie_ins.exists_subset(abc) is False
    
        set_trie_ins.insert(set_trie_ins.create_word(["b"]))
        assert set_trie_ins.exists_subset(abc) is True
    
    def test_set_trie_exists_subset_3(self, set_trie_ins: SetTrie[str]):
        abc = set_trie_ins.create_word(["a", "b", "c"])
        set_trie_ins.insert(set_trie_ins.create_word(["b", "d"]),1)
        set_trie_ins.insert(set_trie_ins.create_word(["d"]), 2)
        assert set_trie_ins.find_subset(abc) is None
        set_trie_ins.insert(set_trie_ins.create_word(["b"]), 3)
        ret = set_trie_ins.find_subset(abc)
        logger.debug(set_trie_ins.root_node)
        logger.debug(ret.tag)
        assert ret is not None and ret.tag == 3

class TestSetTrieExistsSuperset:
    def test_set_trie_exists_superset_1(self, set_trie_ins: SetTrie[str]):
        pass
        # abc = set_trie_ins.create_word(["a", "b", "c"])
        # set_trie_ins.insert(set_trie_ins.create_word(["a", "b"]))
        # set_trie_ins.insert(set_trie_ins.create_word(["a"]))
        # set_trie_ins.insert(set_trie_ins.create_word(["a", "b", "e", "f"]))
        # assert set_trie_ins.exists_superset(abc) is False
        
        # set_trie_ins.insert(set_trie_ins.create_word(["a", "b", "c", "d"]))
        # assert set_trie_ins.exists_superset(abc) is True
    
    def test_set_trie_exists_superset_2(self, set_trie_ins: SetTrie[str]):
        pass
        # abc = set_trie_ins.create_word(["a", "b", "c"])
        # set_trie_ins.insert(set_trie_ins.create_word(["0","a","b","c"]))
        # assert set_trie_ins.exists_superset(abc) is True
