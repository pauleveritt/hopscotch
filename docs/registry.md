# Registry

```{eval-rst}
.. invisible-code-block: python
    from hopscotch.fixtures.dataklasses import Greeting
    from hopscotch.fixtures.dataklasses import AnotherGreeting
    from hopscotch.fixtures.dataklasses import Customer
    from hopscotch.fixtures.dataklasses import FrenchCustomer
```

The registry holds implementations of "kinds of things".
It then lets you retrieve an implementation, possibly doing injection along the way.

## Creating a Registry

It's quite simple to create a registry:

```
>>> from hopscotch import Registry
>>> registry = Registry()

```

You can also create with a parent and with a context.
These are both discussed below.

## Using a Registry

Hopscotch comes from the Pyramid family, which doesn't like module-level globals for the "app".
Usually your registry would become part of your "app" and passed around as needed.

For example, when using `viewdom`, the registry is passed around behind the scenes -- one of the benefits of DI.

## Registering Things

Once you have a registry, you can put something into it "imperatively", meaning, by calling a method on that object.
For example, imagine you had this code:

```{literalinclude} ../src/hopscotch/fixtures/dataklasses.py
---
start-after: Start Greeting
end-at: salutation
```

Maybe `Greeting` ships with your pluggable app.
But you want to allow a local site to replace it with a different greeting:

```{literalinclude} ../src/hopscotch/fixtures/dataklasses.py
---
start-after: Start AnotherGreeting
end-at: salutation
```

Easy: they just grab the registry and register their custom `AnotherGreeting`, telling the registry it's a "kind of" `Greeting`:

```
>>> registry.register(AnotherGreeting, kind=Greeting)

```

As a note, there's nothing magical about dataclasses at this point.
You could just as easily use a "plain old class."

## Kind

What's up with that word "kind"?
At this point, it's a hedge because I can't make up my mind if the registry will be about types.

As we see below, you can `.get` something from the registry.
What is this "something"?
Well, it's the best implementation for the situation, out of the registered implementations.
But you should get back something that, type-wise, is a "kind of" the thing you asked for, to get the developer experience benefits of static analysis.

It would be _great_ if "kind" didn't have to mean "subclass".
You could register things that really had no implementation coupling (inheritance) with the thing they were replacing.
In fact, you could use a `NamedTuple` or even a function.
(Historical fact: you can actually register a function as an implementation of `Greeting`.)

However, tooling -- editors, `mypy` -- will complain that the function isn't really a type-of `Greeting`.
"A-ha" you say, "that's what PEP 544 protocols are for."
That's what I thought too.
But protocols can't be used in all the places a type can -- for example, a `TypeVar`.

So I'm currently stuck with Frankenkind.
For now, it's "subtype."

## Retrieving From A Registry

Super, we now have a place to store implementations.
How do we get one out?

```
>>> greeting = registry.get(Greeting)
>>> greeting.salutation
'Another Hello'

```

Hmm, I got `AnotherGreeting`, not `Greeting`?
Yep.
There were two implementations.
The most recent one -- the second one -- out-prioritized the earlier one (which is still in the registry.)

And another "Hmm"...I got back an instance, not the class.
Yep.
The registry constructs your instances.
These dataclasses had default values on the fields, so nothing was needed.

## Parent Registries

We all work with web-based systems.
There's a startup phase, then when a request comes in, a request-response phase.
The startup information should be setup once, then the per-request information stored and discarded.

Hopscotch has a hierarchical registry.
When you create a registry, you can pass a parent:

```
>>> child_registry = Registry(parent=registry)

```

If you try to get something from the child, it will find the registration in the parent:

```
>>> greeting = child_registry.get(Greeting)
>>> greeting.salutation
'Another Hello'

```

The injector is aware of parentage.
When it goes to get something from the registry, it will walk up until it finds the first match.

```{warning} I'm In Over My Head
Hierarchical registries will ultimately be awesome.
While they work now, it's a "just barely" kind of thing.
Getting it really right -- high performance, lower complexity, caching, and multiprocess -- will be hard.
(But will be worth it.)
```

## Context

Hooray, here's kind of the whole point of Hopscotch: picking the "best" implementation.

In our mythical web system, a request comes in for `/customer/mary`.
I'm just guessing, but we'll probably get the `mary` row from the `Customer` database, as the primary object for that request.
Maybe the `Customer` looks like this:

```{literalinclude} ../src/hopscotch/fixtures/dataklasses.py
---
start-after: Start Customer
end-at: first_name
```

Pyramid makes this a first-class idea called the request "context."
If you put it to use, it's really powerful.
For example, you can register a view that is custom to that "kind of thing."
`wired` also keeps a similar idea in its registry.

Hopscotch does this by letting you, like `wired`, create a registry with an optional `context`:

```
>>> customer = Customer(first_name="mary")
>>> child_registry = Registry(parent=registry, context=customer)
>>> registry.context is None
True
>>> child_registry.context.first_name
'mary'

```

To really see why this is useful, let's start over with a registry that has two registrations:

- A `Greeting` to be used in the general case
- A `AnotherGreeting` to be used when the customer is a `FrenchCustomer`

```
>>> registry = Registry()
>>> registry.register(Greeting)
>>> registry.register(AnotherGreeting, context=FrenchCustomer)

```

A request comes in with no context (or any context that isn't `FrenchCustomer`):

```
>>> child_registry = Registry(parent=registry, context=None)
>>> greeting = registry.get(Greeting)
>>> greeting.salutation
'Hello'

```

Another request comes in -- but it's for a `FrenchCustomer`:

```
>>> customer = FrenchCustomer(first_name="marie")
>>> child_registry = Registry(parent=registry, context=customer)
>>> greeting = child_registry.get(Greeting)
>>> greeting.salutation
'Another Hello'

```

This time when we asked for `Greeting`, we got the registration for `context=FrenchCustomer`.
Why?
Because the child registry was created in a way that was "bound" to that as the registry context.

As a note, you can also manually provide a context when doing a `get`.
Let's use a `FrenchCustomer`, but with the parent registry that was created with `context=None`:

```
>>> greeting = registry.get(Greeting, context=customer)
>>> greeting.salutation
'Another Hello'

```

## Precedence

The registry lets you register multiple implementations of a "kind."
How does the registry decide which to use?

I'll be honest: the current implementation is sketchy, though it has potential.
Basically, it looks through the current registry for matches (before going to the parent.)
It eliminates those that don't match the context.
It then uses a "policy" to decide the best fit.

This can get better/richer/faster in the future.

## Decorator

Imperative registration is definitely not-sexy.
Let's show use of the `@injectable` decorator.

Let's again imagine we have a `Greeting`, but let's show the line _before_ what we showed previously:

```{literalinclude} ../src/hopscotch/fixtures/dataklasses.py
---
start-after: Decorate Greeting
end-at: salutation
```

When we create a registry _this_ time, we'll call `.scan()` to go look for decorators:

```
>>> registry = Registry()
>>> registry.scan()

```

As before, we can later get this:

```{eval-rst}
.. invisible-code-block: python

   # Cheat, because .scan() doesn't work in Sybil.
   registry.register(Greeting)

```

```
>>> greeting = registry.get(Greeting, context=customer)
>>> greeting.salutation
'Hello'

```

`.scan()` can be passed a symbol for a package/module, or a string for a package location.
It's based on the scanner in `venusian` which is a really cool way to defer registration until _after_ import.

## Singletons

Sometimes you don't need an instance constructed.
The data is "outside" the system and there's only one implementation and you already have the instance.
That's where singletons come in.

In Hopscotch you can register a singleton:

```
>>> greeting = Greeting(salutation="I am a singleton")
>>> registry = Registry()
>>> registry.register(greeting)
>>> greeting = registry.get(Greeting)
>>> greeting.salutation
'I am a singleton'

```

You can register a singleton as a "kind" and it will replace a built-in:

```
>>> greeting = AnotherGreeting()
>>> registry = Registry()
>>> registry.register(Greeting)
>>> registry.register(greeting, kind=Greeting)
>>> greeting = registry.get(Greeting)
>>> greeting.salutation
'Hello'

```

Singletons get higher "precedence" than non-singleton registrations.
This helps when you want to say: "Listen, this is the answer in this registry."

```{warning} Is This Dumb?
I went back and forth on whether singletons should use the same method for registering and getting.
I settled on "simpler DX".
But it makes the type hinting harder.
```

## Props

We'll cover this more in [injection](injection), but as a placeholder....when you do a `registry.get()` you can pass in kwargs to use in the construction.
These are called "props", to mimic component-driven development.
