make-it-easy
============

.. image:: https://pypip.in/v/make-it-easy/badge.png
        :alt: Release Status
        :target: https://crate.io/packages/make-it-easy
.. image:: https://pypip.in/d/make-it-easy/badge.png
        :alt: Downloads
        :target: https://crate.io/packages/make-it-easy
.. image:: https://travis-ci.org/dorireuv/make-it-easy.png
        :alt: Build Status
        :target: https://travis-ci.org/dorireuv/make-it-easy

Introduction
============

make-it-easy is a tiny framework that makes it easy to write Test Data Builders in Python.
The framework is a port of the `Java make-it-easy by Nat Pryce`_

.. _Java make-it-easy by Nat Pryce: https://code.google.com/p/make-it-easy/

Test Data Builders are described in the book Growing Object-Oriented Software, Guided by Tests by
Steve Freeman and Nat Pryce. This library lets you write Test Data Builders with much less duplication and
boilerplate code than the approach described in the book.

Installation
============

make-it-easy can be installed using the usual Python packaging tools. It depends on
distribute, but as long as you have a network connection when you install, the
installation process will take care of that for you.

Usage
=====

Basic
-----

Consider the following class hierarchy. This hierarchy illustrates a couple of complicating factors: there is
an abstract base class Fruit and there is a property (ripeness) that is not set via the constructor but by
an operation of the Fruit class.

.. code:: python

 class Fruit(object):
     def __init__(self):
         self._ripeness = 0.0
 
     def ripen(self, ripeness):
         self._ripeness = ripeness
 
     @property
     def is_ripe(self):
         return self._ripeness >= 0.9
 
 
 class Apple(Fruit):
     def __init__(self, num_of_leaves):
         super(Apple, self).__init__()
         self.num_of_leaves = num_of_leaves
 
 
 class Banana(Fruit):
     def __init__(self, curve):
         super(Banana, self).__init__()
         self.curve = curve

Doing so in the style documented in Growing Object-Oriented Software, Guided by Tests would look like this:

.. code:: python

 class AppleBuilder(object):
     def __init__(self):
         self._ripeness = 0.5
         self._leaves = 2
     
     def with_ripeness(self, ripeness):
         self._ripeness = ripeness
         return self
     
     def with_leaves(self, leaves):
         self._leaves = leaves
         return self

     def but(self):
         return AppleBuilder() \
             .with_ripeness(self._ripeness) \
             .with_leaves(self._leaves)
             
     def build(self):
         apple = Apple(self._leaves)
         apple.ripen(self._ripeness)
         return apple
 
 
 class BananaBuilder(object):
     def __init__(self):
         self._ripeness = 0.5
         self._curve = 0.1
     
     def with_ripeness(self, ripeness):
         self._ripeness = ripeness
     
     def with_curve(self, curve):
         self._curve = curve
        
     def but(self):
         return BananaBuilder() \
             .with_ripeness(self._ripeness) \
             .with_curve(self._curve)
             
     def build(self):
         banana = Banana()
         banana.ripen(self._ripeness)
         banana.curve = self._curve
         return banana

 apple_with_two_leaves = AppleBuilder().with_leaves(2)
 ripe_apple = apple_with_two_leaves.but().with_ripeness(0.95)
 unripe_apple = apple_with_two_leaves.but().with_ripeness(0.1)
 
 apple1 = ripe_apple.build()
 apple2 = unripe_apple.build()
 
 
While doing it with make-it-easy can be easy as that:

.. code:: python
 
 from make_it_easy import *
 
 def apple(leaves=2, ripeness=0.0):
     an_apple = Apple(leaves)
     an_apple.ripen(ripeness)
     return an_apple
 
 
 def banana(curve=0.1, ripeness=0.0):
     a_banana = Banana(curve)
     a_banana.ripen(ripeness)
     return a_banana
 
 apple_with_two_leaves = an(apple, with_(2, 'leaves'))
 ripe_apple = apple_with_two_leaves.but(with_(0.95, 'ripeness'))
 unripe_apple = apple_with_two_leaves.but(with_(0.1, 'ripeness'))
 
 apple1 = make(ripe_apple)
 apple2 = make(unripe_apple)

As you can see, with Make It Easy you have to write a lot less duplicated and boilerplate code.

Value Donors
============

Primitives / Makers
-------------------

A value donor is any primitive ('Bob' / 3 / False / etc.) or a `Maker` (the returned object from the a, an functions).
All these can be used as the value in `with_`. For instance a customer `Maker` can be a donor in order `Maker`. It's
important to notice that if a `Maker` is used as a donor, a new instance will be created every time:

.. code:: python

 a_customer = a(customer, with_('Bob', as_('name')))
 an_order = an(order, with_(a_customer, as_('customer')))
 my_order1 = make(an_order)
 my_order2 = make(an_order)
 assert_that(my_order1.customer, is_(instance_of(Customer)))
 assert_that(my_order2.customer, is_(instance_of(Customer)))
 assert_that(my_order1.customer, is_not(same_instance(my_order2.customer)))  # two different instances!!!

The Same Value Donor
--------------------

Sometimes you will need to share the same value while making new data objects, this can be done using `the_same` value
donor. In the following example both my_order1 and my_order2 will have the same customer instance:

.. code:: python

 a_customer = a(customer, with_('Bob', as_('name')))
 an_order = an(order, with_(the_same(a_customer), as_('customer')))
 my_order1 = make(an_order)
 my_order2 = make(an_order)
 assert_that(my_order1.customer, is_(same_instance(my_order2.customer)))

Custom Donors
-------------
In order to create a custom donor, you will simply need to implement the `Donor` interface.

.. code:: python

 class IndexDonor(Donor):
     def __init__(self):
        self._count = itertools.count()

     @property
     def value(self):
        return next(self._count)

 an_indexed_thing = an(an_indexed_thing, with_(IndexDonor(), as_('index')))
 indexed_thing1 = make(an_indexed_thing)
 indexed_thing2 = make(an_indexed_thing)
 assert_that(indexed_thing1.index, is_(equal_to(0)))
 assert_that(indexed_thing2.index, is_(equal_to(1)))

Sequences Donors
----------------
Sometimes we want values to be allocated from a sequence, so we can predict their values or understand where data
has come from in test diagnostics. make-it-easy lets you define a fixed or repeating sequence of values.

A fixed sequence is defined by the `from_` function which expects an iterable:

.. code:: python

 letters = from_("abc")
 assert_that(letters.value, is_(equal_to("a")))
 assert_that(letters.value, is_(equal_to("b")))
 assert_that(letters.value, is_(equal_to("c")))

A fixed sequence of values will fail if asked to provide more elements than are specified when the sequence is created.
A repeating sequence will start back at the beginning of the sequence when all elements are exhausted:

.. code:: python

 letters = from_repeating("ab")
 assert_that(letters.value, is_(equal_to("a")))
 assert_that(letters.value, is_(equal_to("b")))
 assert_that(letters.value, is_(equal_to("a")))
 assert_that(letters.value, is_(equal_to("b")))
 assert_that(letters.value, is_(equal_to("a")))
 assert_that(letters.value, is_(equal_to("b")))

Both fixed and repeating sequences can be created from any iterable (tuple / list / set / dict / etc.).

Calculated Sequences
--------------------
If we do not want to explicitly specify a sequence of values, we can use some convenient base classes to help us
calculate each element of the sequence.
An `IndexedSequence` calculates each element of the sequence from its integer index, starting at zero.

.. code:: python

 class FTagSequence(IndexedSequence):
     def _value_at(self, index):
         return 'f' + "'" * index

 f_tag_sequence = FTagSequence()
 assert_that(f_tag_sequence.value, is_(equal_to("f")))
 assert_that(f_tag_sequence.value, is_(equal_to("f'")))
 assert_that(f_tag_sequence.value, is_(equal_to("f''")))

A ChainedSequence calculates each element of the sequence from the element that preceded it.

.. code:: python

 class FTagChainedSequence(ChainedSequence):
     def _first_value(self):
         return 'f'

     def _value_after(self, prev_value):
         return prev_value + "'"

 f_tag_sequence = FTagChainedSequence()
 assert_that(f_tag_sequence.value, is_(equal_to("f")))
 assert_that(f_tag_sequence.value, is_(equal_to("f'")))
 assert_that(f_tag_sequence.value, is_(equal_to("f''")))