"""Make sure the test/example/docs examples work."""
from hopscotch.fixtures import (
    dataklasses,
    functions,
    named_tuples,
    plain_classes,
    DummyGet,
    init_caller_package,
)


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
    assert dataklasses.GreetingOperator("Hi").salutation == "Hi"
    assert dataklasses.GreetingTuple(("Hi", "Hey")).salutation == ("Hi", "Hey")
    gs = dataklasses.GreetingService()
    assert gs.salutation == "Hello"
    assert dataklasses.Greeter(greeting=greeting).greeting.salutation == "Hello"
    assert dataklasses.GreeterService(greeting=gs).greeting.salutation == "Hello"
    assert dataklasses.GreeterAnnotated(greeting=greeting).greeting.salutation == "Hello"
    assert dataklasses.GreeterChildren(children=tuple()).children == tuple()
    assert dataklasses.GreeterOptional(greeting=None).greeting is None


def test_functions_fixtures() -> None:
    """Check the function examples."""
    greeting = functions.Greeting()
    assert greeting == "Hello"
    assert functions.Greeter(greeting=greeting) == "Hello"
    assert functions.GreetingNoDefault(salutation="Hi") == "Hi"
    assert functions.Greeter(greeting=greeting) == "Hello"
    assert functions.GreeterAnnotated(greeting=greeting) == "Hello"
    assert functions.GreeterChildren(children=tuple()) == tuple()
    assert functions.GreeterOptional(greeting=None) is None


def test_named_tuples_fixtures() -> None:
    """Check the named tuple examples."""
    greeting = named_tuples.Greeting()
    assert greeting.salutation == "Hello"
    assert named_tuples.GreetingNoDefault(salutation="Hi").salutation == "Hi"
    assert named_tuples.Greeter(greeting=greeting).greeting.salutation == "Hello"
    assert named_tuples.GreeterAnnotated(greeting=greeting).greeting.salutation == "Hello"
    assert named_tuples.GreeterChildren(children=tuple()).children == tuple()
    assert named_tuples.GreeterOptional(greeting=None).greeting is None


def test_plain_classes_fixtures() -> None:
    """Check the plain-old-classes examples."""
    greeting = plain_classes.Greeting()
    assert greeting.salutation == "Hello"
    gs = plain_classes.GreetingService()
    assert gs.salutation == "Hello"
    assert plain_classes.GreetingNoDefault(salutation="Hi").salutation == "Hi"
    assert plain_classes.Greeter(greeting=greeting).greeting.salutation == "Hello"
    assert plain_classes.GreeterService(greeting=gs).greeting.salutation == "Hello"
    assert plain_classes.GreeterAnnotated(greeting=greeting).greeting.salutation == "Hello"
    assert plain_classes.GreeterChildren(children=tuple()).children == tuple()
    assert plain_classes.GreeterOptional(greeting=None).greeting is None


def test_dummy_get() -> None:
    """Check the fake operator"""
    dg = DummyGet(arg="Hi")
    assert dg() == "Hi"
