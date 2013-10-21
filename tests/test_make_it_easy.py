import unittest
from hamcrest import *
from make_it_easy import *


class MakeItEasyTestCase(unittest.TestCase):
    def test_uses_default_value_property_values_if_no_properties_were_supplied(self):
        my_apple = make(an(apple))
        assert_that(my_apple.num_of_leaves, is_(equal_to(2)))
        assert_that(my_apple.is_ripe, is_(False))

    def test_overrides_default_values_with_explicit_properties(self):
        my_apple = make(an(apple, with_(3, 'leaves'), with_(0.95, 'ripeness')))
        assert_that(my_apple.num_of_leaves, is_(equal_to(3)))
        assert_that(my_apple.is_ripe, is_(True))

    def test_can_use_maker_to_initialize_property_value(self):
        a_customer = a(customer, with_('Alice', as_('name')))
        an_order = make(an(order, with_(a_customer, as_('customer_'))))
        assert_that(an_order.customer.name, is_(equal_to('Alice')))

    def test_a_distinct_property_value_instance_is_used_for_made_object_when_property_is_defined_with_a_maker(self):
        an_order = an(order, with_(a(customer, with_('Bob', as_('name'))), as_('customer_')))
        my_order1 = make(an_order)
        my_order2 = make(an_order)
        assert_that(my_order1.customer, is_not(same_instance(my_order2.customer)))

    def test_can_explicitly_declare_that_different_instances_have_the_same_property_value_instance(self):
        a_customer = a(customer, with_('Bob', as_('name')))
        an_order = an(order, with_(the_same(a_customer), as_('customer_')))
        my_order1 = make(an_order)
        my_order2 = make(an_order)
        assert_that(my_order1.customer, is_(same_instance(my_order2.customer)))

    def test_distinct_collection_elements_are_used_for_each_made_object_when_elements_are_defined_with_a_maker(self):
        a_fruits_bowl = a(fruits_bowl, with_(list_of(an(apple), a(banana)), 'fruits'))
        fruits_bowl1 = make(a_fruits_bowl)
        fruits_bowl2 = make(a_fruits_bowl)
        assert_that(fruits_bowl1.fruits, is_not(same_instance(fruits_bowl2.fruits)))
        assert_that(fruits_bowl1.fruits[0], is_not(same_instance(fruits_bowl2.fruits[0])))
        assert_that(fruits_bowl1.fruits[1], is_not(same_instance(fruits_bowl2.fruits[1])))

    def test_can_declare_that_elements_of_different_collection_are_the_same(self):
        a_fruits_bowl = a(fruits_bowl, with_(list_of(the_same(apple), the_same(banana)), 'fruits'))
        fruits_bowl1 = make(a_fruits_bowl)
        fruits_bowl2 = make(a_fruits_bowl)
        assert_that(fruits_bowl1.fruits, is_not(same_instance(fruits_bowl2.fruits)))
        assert_that(fruits_bowl1.fruits[0], same_instance(fruits_bowl2.fruits[0]))
        assert_that(fruits_bowl1.fruits[1], same_instance(fruits_bowl2.fruits[1]))

    def test_can_declare_that_same_collection_is_used_for_every_made_object(self):
        a_fruits_bowl = a(fruits_bowl, with_(the_same(list_of(an(apple), a(banana))), 'fruits'))
        fruits_bowl1 = make(a_fruits_bowl)
        fruits_bowl2 = make(a_fruits_bowl)
        assert_that(fruits_bowl1.fruits, is_(same_instance(fruits_bowl2.fruits)))

    def test_can_use_a_maker_as_a_donor(self):
        a_customer = a(customer, with_('Bob', as_('name')))
        an_order = an(order, with_(a_customer, as_('customer_')))
        my_order = make(an_order)
        assert_that(my_order.customer, is_(instance_of(Customer)))

    def test_can_declare_a_maker_as_a_base_maker_using_but(self):
        apple_with_two_leaves = an(apple, with_(2, 'leaves'))
        ripe_apple = apple_with_two_leaves.but(with_(0.95, 'ripeness'))
        unripe_apple = apple_with_two_leaves.but(with_(0.1, 'ripeness'))
        apple1 = make(ripe_apple)
        apple2 = make(unripe_apple)
        assert_that(apple1.is_ripe, is_(True))
        assert_that(apple2.is_ripe, is_(False))


def fruits_bowl(fruits=None):
    return FruitsBowl(fruits or [])


class FruitsBowl(object):
    def __init__(self, fruits):
        self.fruits = fruits


def apple(leaves=2, ripeness=0.0):
    an_apple = Apple(leaves)
    an_apple.ripen(ripeness)
    return an_apple


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


def banana(curve=0.1, ripeness=0.0):
    a_banana = Banana(curve)
    a_banana.ripen(ripeness)
    return a_banana


class Banana(Fruit):
    def __init__(self, curve):
        super(Banana, self).__init__()
        self.curve = curve


def order(customer_=None):
    an_order = Order(customer_ or make(a(customer)))
    return an_order


class Order(object):
    def __init__(self, customer_):
        self._customer = customer_

    @property
    def customer(self):
        return self._customer


def customer(name='Unknown'):
    a_customer = Customer(name)
    return a_customer


class Customer(object):
    def __init__(self, name):
        self.name = name

    @property
    def id(self):
        return self.name