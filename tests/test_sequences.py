import unittest
from hamcrest import *
from hamcrest.core.base_matcher import BaseMatcher
from make_it_easy import *


class MakeItEasyTestCase(unittest.TestCase):
    def test_from_args(self):
        letters = from_("abc")
        assert_that(letters.value, is_(equal_to("a")))
        assert_that(letters.value, is_(equal_to("b")))
        assert_that(letters.value, is_(equal_to("c")))

    def test_from_args_raises_stop_iteration_when_no_more_elements_in_sequence(self):
        letters = from_("ab")
        assert_that(letters.value, is_(equal_to("a")))
        assert_that(letters.value, is_(equal_to("b")))
        self.assertRaises(StopIteration, lambda: letters.value)

    def test_from_repeating(self):
        letters = from_repeating("ab")
        assert_that(letters.value, is_(equal_to("a")))
        assert_that(letters.value, is_(equal_to("b")))
        assert_that(letters.value, is_(equal_to("a")))
        assert_that(letters.value, is_(equal_to("b")))
        assert_that(letters.value, is_(equal_to("a")))
        assert_that(letters.value, is_(equal_to("b")))

    def test_indexed_sequence(self):
        f_tag_sequence = FTagIndexedSequence()
        assert_that(f_tag_sequence.value, is_(equal_to("f")))
        assert_that(f_tag_sequence.value, is_(equal_to("f'")))
        assert_that(f_tag_sequence.value, is_(equal_to("f''")))

    def test_chained_sequence(self):
        f_tag_sequence = FTagChainedSequence()
        assert_that(f_tag_sequence.value, is_(equal_to("f")))
        assert_that(f_tag_sequence.value, is_(equal_to("f'")))
        assert_that(f_tag_sequence.value, is_(equal_to("f''")))


class FTagIndexedSequence(IndexedSequence):
    def _value_at(self, index):
        return 'f' + "'" * index


class FTagChainedSequence(ChainedSequence):
    def _first_value(self):
        return 'f'

    def _value_after(self, prev_value):
        return prev_value + "'"


class _HasItemOfType(BaseMatcher):
    def __init__(self, class_):
        self._class = class_

    def _matches(self, seq):
        for item in seq:
            if isinstance(item, self._class):
                return True

        return False

    def describe_to(self, description):
        description\
            .append_text('item of type ') \
            .append_text(self._class.__name__)


def _has_item_of_type(class_):
    return _HasItemOfType(class_)
