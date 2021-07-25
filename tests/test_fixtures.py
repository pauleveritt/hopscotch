"""Make sure the test/example/docs examples work."""

from hopscotch.fixtures import (
    dataklasses,
    DummyOperator,
    functions,
    init_caller_package,
    named_tuples,
    plain_classes,
)
from hopscotch.registry import Registry


def test_init_caller_package() -> None:
    """Test the fixture at tests.fixtures.init_caller_package."""
    result = init_caller_package.main_package()
    assert init_caller_package == result


def test_dataklass_fixtures() -> None:
    """Check the dataclass examples."""
    greeting = dataklasses.Greeting()
    assert greeting.salutation == "Hello"
    assert dataklasses.GreetingNoDefault(salutation="Hi").salutation == "Hi"
    assert not hasattr(dataklasses.GreetingInitFalse(), "salutation")
    assert dataklasses.GreetingOperator(greeting).greeter.salutation == "Hello"
    assert dataklasses.GreetingTuple(("Hi", "Hey")).salutation == ("Hi", "Hey")
    gs = dataklasses.Greeting()
    assert gs.salutation == "Hello"
    assert dataklasses.Greeter(greeting=greeting).greeting.salutation == "Hello"
    assert dataklasses.GreeterService(greeting=gs).greeting.salutation == "Hello"
    gs2 = dataklasses.GreeterAnnotated(greeting=greeting).greeting.salutation
    assert gs2 == "Hello"
    children = ("a",)
    assert dataklasses.GreeterChildren(children=children).children == children
    assert dataklasses.GreeterOptional(greeting=None).greeting is None
    gi = dataklasses.AnotherGreeting()
    assert gi.salutation == "Another Hello"
    assert isinstance(gi, dataklasses.Greeting)


def test_functions_fixtures() -> None:
    """Check the function examples."""
    greeting = functions.Greeting()
    assert greeting == "Hello"
    assert functions.Greeter(greeting=greeting) == "Hello"
    assert functions.GreetingNoDefault(salutation="Hi") == "Hi"
    assert functions.Greeter(greeting=greeting) == "Hello"
    assert functions.GreeterAnnotated(greeting=greeting) == "Hello"
    children = ("a",)
    assert functions.GreeterChildren(children=children) == children
    assert functions.GreeterOptional(greeting=None) is None


def test_named_tuples_fixtures() -> None:
    """Check the named tuple examples."""
    greeting = named_tuples.Greeting()
    assert greeting.salutation == "Hello"
    assert named_tuples.GreetingNoDefault(salutation="Hi").salutation == "Hi"
    assert named_tuples.Greeter(greeting=greeting).greeting.salutation == "Hello"
    greeter_annotated = named_tuples.GreeterAnnotated(greeting=greeting)
    assert greeter_annotated.greeting.salutation == "Hello"
    children = ("a",)
    assert named_tuples.GreeterChildren(children=children).children == children
    assert named_tuples.GreeterOptional(greeting=None).greeting is None


def test_plain_classes_fixtures() -> None:
    """Check the plain-old-classes examples."""
    greeting = plain_classes.Greeting()
    assert greeting.salutation == "Hello"
    assert plain_classes.GreetingNoDefault(salutation="Hi").salutation == "Hi"
    assert plain_classes.Greeter(greeting=greeting).greeting.salutation == "Hello"
    assert plain_classes.GreeterService(greeting=greeting).greeting.salutation == "Hello"
    greeter_annotated = plain_classes.GreeterAnnotated(greeting=greeting)
    assert greeter_annotated.greeting.salutation == "Hello"
    children = ("a",)
    assert plain_classes.GreeterChildren(children=children).children == children
    assert plain_classes.GreeterOptional(greeting=None).greeting is None


def test_context() -> None:
    """Ensure the ``Customer`` for ``registry.context`` can be constructed."""
    customer = dataklasses.Customer(first_name="Mary")
    assert customer.first_name == "Mary"


def test_french_context() -> None:
    """Ensure construction of ``FrenchCustomer`` for ``registry.context``."""
    customer = dataklasses.FrenchCustomer(first_name="Marie")
    assert customer.first_name == "Marie"


def test_greeter_customer() -> None:
    """Ensure construction of ``GreeterCustomer``."""
    customer = dataklasses.Customer(first_name="Mary")
    greeter = dataklasses.GreeterCustomer(customer=customer)
    assert greeter.customer.first_name == "Mary"


def test_greeter_french_customer() -> None:
    """Ensure construction of ``GreeterFrenchCustomer``."""
    customer = dataklasses.FrenchCustomer(first_name="Marie")
    greeter = dataklasses.GreeterFrenchCustomer(customer=customer)
    assert greeter.customer.first_name == "Marie"


def test_dummy_get() -> None:
    """Check the fake operator."""
    dg = DummyOperator(arg="Hi")
    registry = Registry()
    assert dg(registry) == "Hi"
