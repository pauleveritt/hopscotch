# Injection

Hopscotch has two faces: a registry for implementations _and_ a dependency injector for construction.

What does that even mean?

In Hopscotch, here's the flow:

- Something asks for a "kind of thing"...maybe a component asks for a subcomponent
- The registry gets the best implementation
- The registry then _calls_ that implementation, supplying it the arguments it is asking for
- Some of those arguments might be "kinds of things" which also need instances
- Later, when I'm brave, this will all be cached and persistent

If _registries_ are an "OMG too much magic" thing in Python, then dependency injection is a "you're trying to make this into Java" kind of thing.
In Hopscotch, I want to show we can lower the bar to make the simple case really simple, especially for consumers.

Let's roll.

## The Simplest Case

```{eval-rst}
.. invisible-code-block: python
    from hopscotch import Registry
    from hopscotch.fixtures.dataklasses import Greeting
    from hopscotch.fixtures.dataklasses import Greeter
    from hopscotch.fixtures.dataklasses import AnotherGreeting
    from hopscotch.fixtures.dataklasses import GreeterGetAnother
    from hopscotch.fixtures.dataklasses import GreeterFirstName
    from hopscotch.fixtures.dataklasses import Customer
```

We have a `Greeter` who says hello with a greeting.
Actually, a `Greeting` -- an instance of a class that is in "the system".

```{literalinclude} ../src/hopscotch/fixtures/dataklasses.py
---
start-after: Start Greeter
end-at: greeting
```

We can make a pluggable which has `Greeting` and `Greeter` in its registry:

```
>>> from hopscotch import Registry
>>> registry = Registry()
>>> registry.scan()

```

```{eval-rst}
.. invisible-code-block: python

   # Cheat, because .scan() doesn't work in Sybil.
   registry.register(Greeting)
   registry.register(Greeter)

```

Now that we're all setup, let's ask for a `Greeter`:

```
>>> greeter = registry.get(Greeter)
>>> greeter.greeting.salutation
'Hello'

```

What happened?

- We asked the registry for `Greeter`
- It found the "best-fit" implementation...in this case, `Greeter` itself
- The registry started constructing an instance by introspecting its fields
- The `Greeter.greeting` field had a type hint of `Greeting`
- The registry had an implementation for `Greeting`
- Since `Greeting` had a default value for its one field, it could be constructed
- The registry used that constructed instance to construct `Greeter`
- Done

"Woah, dataclass magical mumbo jumbo!" you say.
Well, here's an example using a plain-old-class:

```{literalinclude} ../src/hopscotch/fixtures/plain_classes.py
---
start-after: Start Greeter
end-at: self.greeting
```

Here's a `NamedTuple`:

```{literalinclude} ../src/hopscotch/fixtures/named_tuples.py
---
start-after: Start Greeter
end-at: greeting
```

...but with a caveat: `NamedTuple` and functions (next) have a little sharp edge regarding the "kind" discussion in [](registry).
Here's a function for `Greeter` that can also be dependency injected:

```{literalinclude} ../src/hopscotch/fixtures/named_tuples.py
---
start-after: Start Greeter
end-at: greeting
```

Even for the "simple" case, this is pretty valuable.
Really de-coupled systems, where you can add things without monkey-patching and the callees get to decide what they need.

## Manual Factory

"Too much magic!"
It's true that the injector has a good number of policy decisions in the service of "helping."
Perhaps you'd like to keep injection, but have manual control over construction?
For that, provide a class method named `__hopscotch_factory`:

```{literalinclude} ../src/hopscotch/fixtures/dataklasses.py
---
start-after: Start GreetingFactory
end-at: salutation=
```

## Generics

Hopscotch injection works by the type hint.
Provide a type, Hopscotch tries to go get it and make an instance for you.
But those type hints can be...rich.
Here's a `Greeter` who can have an optional `Greeting`:

```{literalinclude} ../src/hopscotch/fixtures/dataklasses.py
---
start-after: Start GreeterOptional
end-at: no default
```

Dataclasses especially have some extra generics to cover their fields.

## Default Values

When you're constructing or calling something -- dataclass, plain old class, NamedTuple, function -- the parameters might have default values.

A dataclass might have a field with a default value:

```{literalinclude} ../src/hopscotch/fixtures/dataklasses.py
---
start-after: Start Greeting
end-at: Hello
```

But so might a function:

```{literalinclude} ../src/hopscotch/fixtures/functions.py
---
start-after: Start GreeterOptional
end-at: return greeting
```

The default value is the lowest-precedence option.
The injector tries to go get a value from the registry based on the field/parameter's type.
In these two cases, the type hint says `str` which, obviously, won't be in the registry.

## Operators

Now, on to the part where Hopscotch actually adds to the status quo.

In some cases, we want a little transform between what we're asking for and what we're getting.
For example, perhaps we have a registry with a context:

```
>>> registry = Registry()
>>> registry.register(Greeting)
>>> registry.register(AnotherGreeting, kind=Greeting)
>>> registry.register(Greeter)

```

We'd like to get `Greeting` out, but we know it's really going to be `AnotherGreeting`.
For this we can use an "operator": a simple callable class which is given some inputs and returns an output:

```{eval-rst}
.. invisible-code-block: python
    registry.register(GreeterGetAnother, kind=Greeter)
```

```{literalinclude} ../src/hopscotch/fixtures/dataklasses.py
---
start-after: Start GreeterGetAnother
end-at: AnotherGreeting
```

What is `get`?
It's an "operator":

```{literalinclude} ../src/hopscotch/operators.py
---
start-after: Start Get
end-at: return result_value
```

In this case, we're saying: "Sure, go get me a `Greeting`, but actually, I know it is a `AnotherGreeting`."

Here's a super-useful variation: get me a `Greeting` and then pluck the attribute I'm really looking for:

```{literalinclude} ../src/hopscotch/fixtures/dataklasses.py
---
start-after: Start GreeterFirstName
end-at: customer_name
```

Let's see it in action. I have a registry which registers a `Customer` singleton and `GreeterFirstName`, then gets a `Greeter`:

```
>>> registry = Registry()
>>> customer = Customer(first_name="Mary")
>>> registry.register(customer)  # A singleton
>>> registry.register(GreeterFirstName, kind=Greeter)
>>> greeter = registry.get(Greeter)
>>> greeter.customer_name
'Mary'

```

Operators act like a DSL, giving instructions to the injector.
Since you can very easily write your own, it provides a nice way to concentrate your injectables on what they _really_ need.
Minimizing the surface area with the outside system has benefits.

## Annotated

We just discussed operators.
I lied a little: `get` isn't strictly an operator.
It's actually a `dataclasses.field` which stuffs some expected values -- namely, `operator` -- in the metadata part of a `field`.

This is actually syntactic sugar over a more verbose form that can be used _outside_ dataclasses: plain old classes, `NamedTuple`, and even functions.
For example, here's a function that asks the registry to get the `Customer` and pluck the `first_name`:

```{literalinclude} ../src/hopscotch/fixtures/functions.py
---
start-after: Start GreeterAnnotated
end-at: return customer_name
```

Previously, the `dataclasses.field` metadata communicated with the injector.
This uses [PEP 593 -- Flexible function and variable annotations](https://www.python.org/dev/peps/pep-0593/) to give injector instructions.
The `NamedTuple` and plain old classes also use this.
In fact, dataclasses can use `Annotated` also, though there's no real reason to.
As long as the operator has a "field" version -- `Get` vs. `get` -- it's a lot more convenient to use the latter.

## Context

Sometimes you want to inject a field that has an attribute off the context.
You can't just say `get(Context)` as there isn't a `Context` class registered on the registry.
Instead, it's an attribute.

Instead, there's another operator for this: the `Context` operator with its `context` field:

```{literalinclude} ../src/hopscotch/fixtures/dataklasses.py
---
start-after: Start GreeterFrenchCustomer
end-at: = context
```

This does the moral equivalent of grabbing `registry.context`.
It also supports passing in `attr=` to pluck just one attribute.

## Props

We've seen how Hopscotch can gather the inputs needed to construct an instance: symbols in the registry, operators that return values, default values, etc.

Hopscotch was written to power `ViewDOM` and its software for component-driven development.
In frontends, components are usually passed "props" in a particular usage.
Hopscotch also allows "props": values passed in during `registry.get()` which have the highest precedence.

Here's an example of a registry with a `Greeting`:

```
>>> registry = Registry()
>>> registry.register(Greeting)

```

I'm now in a request and, for some reason, I want to supply a specific `salutation`, as a "prop":

```
>>> greeting = registry.get(Greeting, salutation="Hello Prop")
>>> greeting.salutation
'Hello Prop'

```

What would that look like in ViewDOM?
In a template somewhere, you'd say: `<{Greeting} salutation="Hello Prop" //>`.

## Same Ol' Dataclasses

As can be inferred, dataclasses are the "first-class citizen."
As such, there's several aspects that are accommodated.
For example, fields that should be handled in a `__post_init__` are deferred to let the dataclass handle that field, rather than injecting it.

## inject_callable

ViewDOM works well with Hopscotch, but doesn't require it.
You can have some utility components as functions that aren't in the registry, because of the whole type/kind thing.
Or, you can just skip completely the "replaceable components" thing and just rely in symbols as the only implementation.

For this, Hopscotch lets you use the injector independently of the registry via the `hopscotch.inject_callable` function.
It's a bit more work: you have to supply a `Registration` object that is the result of introspecting the target to be constructed.
(There's a function for that too.)
