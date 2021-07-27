"""Type-oriented registry that start simple and finishes powerful."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from importlib import import_module
from inspect import isclass
from types import ModuleType
from typing import Any
from typing import Callable
from typing import Optional
from typing import Type
from typing import TypedDict
from typing import TypeVar
from typing import Union

from venusian import attach
from venusian import Scanner

from .callers import caller_package
from .field_infos import FieldInfos
from .field_infos import get_field_infos

PACKAGE = Optional[Union[ModuleType, str]]
Props = dict[str, Any]


@dataclass()
class Registration:
    """Collect registration and introspection info of a target."""

    slots = ("implementation", "servicetype", "context", "field_infos", "is_singleton")
    implementation: Union[Callable[..., object], object]
    servicetype: Optional[Callable[..., object]] = None
    context: Optional[Callable[..., object]] = None
    field_infos: FieldInfos = field(default_factory=list)
    is_singleton: bool = False

    def __post_init__(self) -> None:
        """Extract and assign the field infos if not singleton."""
        if not self.is_singleton:
            self.field_infos = get_field_infos(self.implementation)


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
        is_builtin = field_info.is_builtin
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
        elif not is_builtin:
            # Avoid trying to inject str, meaning, only inject
            # user-defined classes
            # TODO If ``ft`` is a function or NamedTuple, it kind of breaks
            #   the type-oriented contract for ``get``. But the following
            #   might still work.  Not sure the right solution.
            if registry:
                field_value = registry.get(ft)
            else:
                # Treat this as a symbol that can be injected without
                # a lookup, such as a function, NamedTuple, etc.
                # TODO Would be great to avoid computing this each time
                registration = Registration(
                    context=None,  # TODO Bring this back w/ context injection
                    implementation=ft,
                    is_singleton=False,  # TODO They might be in registry
                )
                field_value = inject_callable(registration, props=props)
        elif field_info.default_value is not None:
            field_value = field_info.default_value
        else:
            ql = target.__qualname__  # type: ignore
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
    """Factory for defaultdict to initialize second level of tree."""
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

    def get(  # noqa: C901
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

        st_registrations = self.registrations[servicetype]
        if kwargs:
            # If props are passed in, we can't use singletons. So if
            # kwargs are None, add in singletons.
            registrations = st_registrations["classes"]
        else:
            registrations = st_registrations["singletons"] | st_registrations["classes"]

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
                precedences2["low"] = these_registrations
            elif this_context is context_class:
                precedences2["high"] = these_registrations
            elif this_context is None:
                precedences2["low"] = these_registrations
            elif context_class is not None and issubclass(context_class, this_context):
                precedences2["medium"] = these_registrations
            # Otherwise, filter it out and do nothing

        # Now filter by predicates
        matches = precedences2["high"] + precedences2["medium"] + precedences2["low"]
        for match in matches:
            if match.is_singleton:
                # TODO Now that ``.get()`` makes promises about typing, it makes
                #    registering a singleton for a "kind" a good bit harder.
                #    We'll just shut this up for now.
                return match.implementation  # type: ignore
            else:
                # Need to construct it
                instance: T = self.inject(match, props=kwargs)
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
        s_or_c = "singletons" if is_singleton else "classes"
        registrations = self.registrations[st][s_or_c]  # type: ignore
        registrations[context].insert(0, registration)


class injectable:  # noqa
    """``venusian`` decorator to register an injectable factory ."""

    servicetype = None  # Give subclasses a chance to give default, e.g. view

    def __init__(
        self,
        servicetype: Optional[Type[T]] = None,
        *,
        context: Optional[Optional[Any]] = None,
    ):
        """Construct decorator that can register later with registry."""
        if servicetype is not None:
            self.servicetype = servicetype
        self.context = context

    def __call__(self, wrapped: object) -> object:
        """Execute the decorator during venusian scan phase."""

        def callback(scanner: Scanner, name: str, cls: object) -> None:
            """Perform the work of actually putting in registry."""
            servicetype = self.servicetype if self.servicetype else cls
            registry = getattr(scanner, "registry")
            registry.register(
                implementation=cls,
                servicetype=servicetype,
                context=self.context,
            )

        attach(wrapped, callback)
        return wrapped
