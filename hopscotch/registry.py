"""Type-oriented registry that start simple and finishes powerful."""
from __future__ import annotations

from abc import ABCMeta
from collections import defaultdict
from dataclasses import dataclass, field
from importlib import import_module
from inspect import isclass
from types import ModuleType
from typing import Any, Optional, Type, TypeVar, Union, TypedDict

from venusian import Scanner

from .callers import caller_package
from .field_infos import get_field_infos, FieldInfos

PACKAGE = Optional[Union[ModuleType, str]]
Props = dict[str, Any]


@dataclass()
class TreeNode:
    """A servicetype with registered singletons and classes."""

    servicetype: type
    singletons: list[type] = field(default=list)
    classes: list[type] = field(default=list)


@dataclass()
class Registration:
    """Collect registration and introspection info of a target."""

    slots = ("implementation", "servicetype", "context", "field_infos", "is_singleton")
    implementation: Union[Type[T], T]
    servicetype: Optional[Type[T]] = None
    context: Optional[type] = None
    field_infos: FieldInfos = field(default_factory=list)
    is_singleton: bool = False

    def __post_init__(self) -> None:
        """Extract and assign the field infos if not singleton."""
        if not self.is_singleton:
            self.field_infos = get_field_infos(self.implementation)


class Service(metaclass=ABCMeta):
    """Type-oriented base class that supports looking up implementations."""

    pass


T = TypeVar("T")


def inject_callable(
        registration: Registration,
        props: Optional[Props] = None,
        registry: Optional[Registry] = None,
) -> T:
    """Construct target with or without a registry."""

    target = registration.implementation
    kwargs = {}

    # If the target has a ``__hopscotch_factory__``, use that instead
    # of automated construction.
    factory = getattr(target, "__hopscotch_factory__", None)

    if factory is not None and registry is not None:
        # TODO Allow usage without a registry
        result: T = factory(registry)
        return result

    # Does the registry already have field info for this target?
    if registry is not None:
        these_field_infos = registration.field_infos
    else:
        # No registry, so we calculate field info every time (boo)
        these_field_infos = get_field_infos(target)

    for field_info in these_field_infos:
        fn = field_info.field_name
        ft = field_info.field_type
        operator = field_info.operator
        if props and fn in props:
            # Props have highest precedence
            field_value = props[fn]
        elif operator is not None and registry is not None:
            # FIXME Put a single registry is not None wrapper around
            #   the next 3 statements.
            # This field uses Annotated[SomeType, SomeOperator]
            field_value = operator(registry)
        elif registry and ft is Registry:
            # Special rule: if you ask for the registry, you'll get it
            field_value = registry
        elif registry and ft.__module__ != "builtins":
            # Avoid trying to inject str, meaning, only inject
            # user-defined classes
            field_value = registry.get(ft)
        elif field_info.default_value is not None:
            field_value = field_info.default_value
        else:
            ql = target.__qualname__
            msg = f"Cannot inject '{ft.__name__}' on '{ql}.{fn}'"
            raise ValueError(msg)

        kwargs[fn] = field_value

    # Construct and return the class
    return target(**kwargs)  # type: ignore


class KindGroups(TypedDict):
    """Constrain the keys to just singleton and classes."""
    singletons: dict[Union[type, Type[None]], list[Registration]]
    classes: dict[Union[type, Type[None]], list[Registration]]


def make_singletons_classes() -> KindGroups:
    """Factory for defaultdict to initialize second level of tree"""
    kind_groups: KindGroups = dict(
        singletons=defaultdict(list),
        classes=defaultdict(list),
    )
    return kind_groups


Registrations = dict[type, KindGroups]


class Registry:
    """Type-oriented registry with special features."""
    context: Optional[Any]
    parent: Optional[Registry]
    scanner: Scanner
    registrations: Registrations

    def __init__(
            self,
            parent: Optional[Registry] = None,
            context: Optional[Any] = None,
    ) -> None:
        """Construct a registry that might have a context and be nested."""
        self.classes: dict[type, list[type]] = defaultdict(list)
        self.registrations = defaultdict(make_singletons_classes)
        self.parent: Optional[Registry] = parent
        self.context = context
        self.scanner = Scanner(registry=self)

    def scan(
            self,
            pkg: PACKAGE = None,
    ) -> None:
        """Look for decorators that need to be registered."""
        if pkg is None:
            # Get the caller module and import it
            pkg = caller_package()
        elif isinstance(pkg, str):
            # importlib.resource package specification
            pkg = import_module(pkg)
        self.scanner.scan(pkg)

    def inject(self, registration: Registration, props: Optional[Props] = None) -> T:
        """Use injection to construct and return an instance."""
        return inject_callable(registration, props=props, registry=self)

    def get(
            self,
            servicetype: Type[T],
            context: Optional[Any] = None,
            **kwargs: Props,
    ) -> T:
        """Find an appropriate service class and construct an implementation.

        The passed-in keyword args act as "props" which have highest-precedence
        as arguments used in construction.
        """

        # Use the passed-in context class if provided, otherwise, the
        # the registry's context (if provided.)
        context_class: Optional[Any] = None
        if context:
            context_class = context.__class__
        elif self.context:
            context_class = self.context.__class__

        # Look registrations for servicetypes that are an exact match
        # (higher precedence) vs. subclass (lower precedence) vs.
        # no match.
        matching_servicetypes: dict[str, dict]

        st_registrations = self.registrations[servicetype]
        if kwargs:
            # If props are passed in, we can't use singletons. So if
            # kwargs are None, add in singletons.
            registrations = st_registrations['classes']
        else:
            registrations = st_registrations['singletons'] | st_registrations['classes']

        # We will put possible matches into three piles: high/medium/low
        # precedence. Each pile is an ordered list based on registration
        # time (later registrations override earlier.)
        precedences2: dict[str, list[Registration]] = dict(
            high=list(),
            medium=list(),
            low=list(),
        )
        for this_context, these_registrations in registrations.items():
            if this_context is None and context_class is None:
                # This is the most basic case, test it first to bail out quickly.
                precedences2['low'] = these_registrations
            elif this_context is context_class:
                precedences2['high'] = these_registrations
            elif this_context is None:
                precedences2['low'] = these_registrations
            elif context_class is not None and issubclass(context_class, this_context):
                precedences2['medium'] = these_registrations
            # Otherwise, filter it out and do nothing

        # Now filter by predicates
        matches = precedences2['high'] + precedences2['medium'] + precedences2['low']
        for match in matches:
            if match.is_singleton:
                return match.implementation
            else:
                # Need to construct it
                instance = self.inject(match, props=kwargs)
                return instance

        # # Try with the parents
        if self.parent is not None:
            return self.parent.get(servicetype, context, **kwargs)

        # If we get to here, we didn't find anything, raise an error
        msg = f"No service '{servicetype.__name__}' in registry"
        raise LookupError(msg)

    def register(
            self,
            implementation: Union[T, Type[T]],
            *,
            servicetype: Optional[Type[T]] = None,
            context: Optional[Any] = None,
    ) -> None:
        """Use a LIFO list for all the possible implementations.

        Note that the implementation must be a subclass of the servicetype.
        """
        is_singleton = not isclass(implementation)
        registration = Registration(
            implementation=implementation,
            context=context,
            servicetype=servicetype,
            is_singleton=is_singleton,
        )

        # Let's decide what key to use to register this as.
        if servicetype is None:
            st = type(implementation) if is_singleton else implementation
        else:
            st = servicetype

        # Put this in the correct place of the registrations tree,
        # creating tree nodes as needed.
        s_or_c = 'singletons' if is_singleton else 'classes'
        self.registrations[st][s_or_c][context].insert(0, registration)
