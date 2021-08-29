# Why `Hopscotch`?

I'm not convinced the world of Python wants registries (though they should.)
I'm _really_ not convinced Python wants _another_ registry package -- there are already several, some that come really close to what I wanted.
Registry _plus_ dependency injection?

C'mon, man.

This document tries to explain what itches are being scratched in Hopscotch.
Remember: I don't actually expect this stack of software to get adopted.
It's primarily for me to learn and articulate some ideas from the world of frontend development.

## Why Not?

I'll start here.
Things like registries are an indirection.
All frameworks are by definition an indirection -- some mysterious force is calling your code and passing in arguments.
Have you ever written a pytest test?
If so, a registry is calling your code and even doing dependency injection!

Still, registries have a bad rap in Python.
Inversion of control, dependency injection -- hell, when even type hints are "too much ceremony", you know something like Hopscotch is in left field.

Though times are kind of changing, thanks to FastAPI and its cohort.

## Pluggable Apps

My background in Zope has baked into my consciousness a love of pluggable apps.
What's that?
A "mostly done", out-of-the-box (OOTB) system with pieces that can be extended (add), replaced (overwritten), _and_ varied (multiple implementations from which best-fit is chosen.)
If you've ever used Pyramid and seen its predicates -- that's what I mean.

As an example, imagine a Sphinx (pluggable app) using a theme (plugin) in a site (local customization.)
I'd like to change the breadcrumbs, but _only_ in one class of thing, or one part of the site.

## Fail Faster

I want static analysis to help drive a better developer experience.
Sitting in an editor, I want red warnings when I do something wrong.

"Convention over configuration", with its magically-named variables and files, flies in the face of this.
I want to see how far I can go with pluggable systems that express the lines you can paint within, via a smart editor.

## Tooling

In a related sense, I want CI to tell me -- or even better, people extending or using my downstream system -- when the rules are broken.
If you've ever written a Sphinx extension, you'll know -- it's magical names all the way down.

## Caller-Callee Decoupling

Again in Sphinx, if I want to extend something and there wasn't a specially-designed facility (e.g. "put your list of sidebars here as strings"), then I have to fork/monkeypatch the caller.
If I'm writing to a plug point, and I need more information than what it will pass me, I have to...fork the caller.

Forking the caller is bad.

So instead, pluggable systems pass around a universe object, where you can get everything (the Sphinx app, the request object.)

## Small Surface Area

This is also bad.
The callee now has a contract that's...kind of big.
They might get passed more arguments than they want.
It certainly makes test writing a contemplative exercise.

I want my callable arguments to say exactly what I depend on, no more, no less.

And later, I might want to cache/persist the results.
In that case, I _really_ don't want to depend on the universe.
How do you hash the universe?

## Opportunities

Registry-driven injection has some opportunities for fun ideas.

Frontend development is very, very rich in innovation.
Views driven by immutable-state stores as reactive observers...it's not overkill, it's actually fodder for some real leaps forward.

One of my biggest goals is to have a component (injectable) constructed by "the system" which tracks what you depended on.
If anything changes, we regenerate you, immutably.
If you're building a Sphinx site, you might render breadcrumbs once for a folder, and other items therein will use it.

And then, persist that rendered component, so when you wake up next time...if nothing changed, you're already built.

There are other places for cool thinking, like...[htmx](https://www.htmx.org).
If the things you depend on are replaceable, you might have a "Layout" component which knows how to write fragments to disk.
Then, getting your htmx-driven views let you fetch smaller payloads.

## Yeh, Sure, Back to `jinja2`

It's asking too much for people to rethink templating in Python.
But, I'll tinker with it anyway.
