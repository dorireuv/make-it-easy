# make_it_easy.py

# A tiny framework that makes it easy to write Test Data Builders in Python
# Copyright (C) 2013 Dori Reuveni
# E-mail: dorireuv AT gmail DOT com

# make-it-easy 1.0.3
# https://www.github.com/dorireuv/make-it-easy

# Released subject to the Apache License (2.0)
# Please see http://www.apache.org/licenses/LICENSE-2.0.html


__all__ = (
    'a',
    'an',
    'with_',
    'the_same',
    'make',
    'list_of',
    'set_of',
    'tuple_of',
    'as_',
    'from_',
    'from_repeating',
    'IndexedSequence',
    'ChainedSequence',
)


from abc import ABCMeta, abstractproperty, abstractmethod


def a(instantiator, *properties):
    return Maker(instantiator, _convert_properties_to_property_lookup(*properties))


def an(instantiator, *properties):
    return a(instantiator, *properties)


def with_(value, name):
    return Property(name, value)


def the_same(donor_or_instantiator, *properties):
    if isinstance(donor_or_instantiator, Donor):
        donor = donor_or_instantiator
        return SameValueDonor(donor.value)
    else:
        instantiator = donor_or_instantiator
        return SameValueDonor(an(instantiator, *properties))


def make(maker):
    return maker.make()


def list_of(*properties):
    return SeqOfProperties(properties, list)


def set_of(*properties):
    return SeqOfProperties(properties, set)


def tuple_of(*properties):
    return SeqOfProperties(properties, tuple)


def as_(name):
    return name


def from_(iterable):
    return ElementsSequence(iterable, [])


def from_repeating(iterable):
    return ElementsSequence(iterable, iterable)


class Donor(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def value(self):
        raise NotImplementedError()


class SameValueDonor(Donor):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value


class Maker(Donor):
    def __init__(self, instantiator, lookup):
        self._instantiator = instantiator
        self._lookup = lookup

    def make(self):
        return self._instantiator(**self._lookup)

    def with_(self, value, name):
        if not isinstance(value, Donor):
            value = SameValueDonor(value)

        self._lookup[name] = value
        return self

    def but(self, *properties):
        lookup = _PropertyLookup()
        lookup.update(self._lookup)
        lookup.update(_convert_properties_to_property_lookup(*properties))
        return Maker(self._instantiator, lookup)

    @property
    def value(self):
        return self.make()


class SeqOfProperties(Donor):
    def __init__(self, iterable, seq_class):
        self._donors = tuple(map(_convert_value_to_donor, iterable))
        self._seq_class = seq_class

    @property
    def value(self):
        return self._seq_class(map(lambda donor: donor.value, self._donors))


class Property(object):
    def __init__(self, name, value):
        self._name = name
        self._donor = _convert_value_to_donor(value)

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._donor


class ChainedSequence(Donor):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._is_first = True
        self._prev_value = None

    @property
    def value(self):
        if self._is_first:
            self._is_first = False
            res = self._first_value()
        else:
            res = self._value_after(self._prev_value)

        self._prev_value = res
        return res

    @abstractmethod
    def _first_value(self):
        raise NotImplementedError()

    @abstractmethod
    def _value_after(self, prev_value):
        raise NotImplementedError()


class IndexedSequence(Donor):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._index = 0

    @property
    def value(self):
        res = self._value_at(self._index)
        self._index += 1
        return res

    @abstractmethod
    def _value_at(self, index):
        raise NotImplementedError()


class ElementsSequence(Donor):
    def __init__(self, iterable, next_iterable):
        self._next_iterable = next_iterable
        self._current = iter(iterable)

    @property
    def value(self):
        try:
            return next(self._current)
        except StopIteration:
            self._current = iter(self._next_iterable)
            return next(self._current)


class _PropertyLookup(object):
    def __init__(self):
        self._lookup = dict()

    def __getitem__(self, key):
        return self._lookup[key].value

    def __setitem__(self, key, value):
        self._lookup[key] = value

    def get(self, key, default_value=None):
        if key in self:
            return self.__getitem__(key)
        else:
            return default_value

    def keys(self):
        return self._lookup.keys()

    def iteritems(self):
        return _iteritems(self._lookup)

    def update(self, other_property_lookup):
        return self._lookup.update(other_property_lookup.iteritems())


def _convert_value_to_donor(value):
    if not isinstance(value, Donor):
        value = SameValueDonor(value)

    return value


def _convert_properties_to_property_lookup(*properties):
    lookup = _PropertyLookup()
    for property_ in properties:
        lookup[property_.name] = property_.value

    return lookup


def _iteritems(d):
    """Factor-out Py2-to-3 differences in dictionary item iterator methods"""
    try:
        return d.iteritems()
    except AttributeError:
        return d.items()