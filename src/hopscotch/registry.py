"""Type-oriented registry that start simple and finishes powerful."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from importlib import import_module
from inspect import getmro
from inspect import isclass
from types import ModuleType
from typing import Any
from typing import Callable
from typing import cast
from typing import Optional
from typing import Type
from typing import TypedDict
from typing import TypeVar
from typing import Union

from venusian import attach
from venusian import Scanner

from .callers import caller_package
from .field_infos import FieldInfo
from .field_infos import FieldInfos
from .field_infos import get_field_infos

PACKAGE = Optional[Union[ModuleType, str]]
Props = dict[str, Any]


class IsNoneType:
    """Mimic Python 3.10 ``NoneType`` as just a marker."""

    pass


@dataclass()
class Registration:
    """Collect registration and introspection info of a target."""

    slots = ("implementation", "kind", "context", "field_infos", "is_singleton")
    implementation: Union[Callable[..., object], object]
    kind: Optional[Callable[..., object]] = None
    context: Optional[Callable[..., object]] = None
    field_infos: FieldInfos = field(default_factory=list)
    is_singleton: bool = False

    def __post_init__(self) -> None:
        """Extract and assign the field infos if not singleton."""
        if not self.is_singleton:
            self.field_infos = get_field_infos(self.implementation)


T = TypeVar("T")


def inject_field_no_registry(
    field_info: FieldInfo,
    props: Optional[Props],
) -> Optional[object]:
    """Get a value for a field without a registry."""
    ft = field_info.field_type
    is_builtin = field_info.is_builtin
    if not (ft is None or is_builtin):
        # Avoid trying to inject str, meaning, only inject
        # user-defined classes
        # Treat this as a symbol that can be injected without
        # a lookup, such as a function, NamedTuple, etc.
        # TODO Would be great to avoid computing this each time
        registration = Registration(
            context=None,
            implementation=ft,
            is_singleton=False,  # TODO They might be in registry
        )
        return inject_callable(registration, props=props)

    return None


def inject_field_registry(
    field_info: FieldInfo,
    registry: Registry,
) -> Optional[Any]:
    """Get a value for a field using a registry."""
    ft = field_info.field_type
    is_builtin = field_info.is_builtin
    operator = field_info.operator
    if operator is not None:
        # This field uses Annotated[SomeType, SomeOperator]
        return operator(registry)
    elif ft is Registry:
        # Special rule: if you ask for the registry, you'll get it
        return registry
    elif not (ft is None or is_builtin):
        # Avoid trying to inject str, meaning, only inject
        # user-defined classes
        # TODO If ``ft`` is a function or NamedTuple, it kind of breaks
        #   the type-oriented contract for ``get``. But the following
        #   might still work.  Not sure the right solution.
        try:
            return registry.get(ft)
        except LookupError as exc:
            # See if this dependency is in parent registries
            if registry.parent:
                return registry.parent.get(ft)
            # No parent registry, just re-raise the exception
            raise exc

    return None


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
        result: T = factory(registry)
        return result

    for field_info in registration.field_infos:
        fn = field_info.field_name
        if props and fn in props:
            # Props have highest precedence
            field_value = props[fn]
        elif registry:
            try:
                field_value = inject_field_registry(field_info, registry)
            except LookupError:
                # During *injection* (not during ``registry.get``) we
                # allow injectable dependencies that aren't registered.
                # Maybe a function, dataclass, whatever. Just inject it.
                field_value = inject_field_no_registry(field_info, props)
        else:
            field_value = inject_field_no_registry(field_info, props)

        # If we didn't get a value...
        if field_value is None:
            if field_info.default_value is not None:
                # ...try to get from default
                field_value = field_info.default_value
            elif field_info.default_factory is not None:
                field_value = field_info.default_factory()
            else:
                # ...otherwise, we failed injection.
                ql = target.__qualname__  # type: ignore
                ft = field_info.field_type
                ft_name = "None" if ft is None else ft.__name__
                msg = f"Cannot inject '{ft_name}' on '{ql}.{fn}'"
                raise ValueError(msg)

        kwargs[fn] = field_value

    # Construct and return the class
    return target(**kwargs)  # type: ignore


class KindGroups(TypedDict):
    """Constrain the keys to just singleton and classes."""

    singletons: dict[Union[type, IsNoneType], list[Registration]]
    classes: dict[Union[type, IsNoneType], list[Registration]]


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
        if context is None and parent is not None:
            self.context = parent.context
        else:
            self.context = context
        self.scanner = Scanner(registry=self)

    def setup(
        self,
        pkg: PACKAGE = None,
    ) -> None:
        """Pass the registry to a package which has a setup function."""
        setup_function = getattr(pkg, "hopscotch_setup", None)
        if setup_function:
            setup_function(self)

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

    def get_best_match(
        self,
        kind: Type[T],
        context_class: Optional[Any] = None,
        allow_singletons: bool = True,  # If props are passed in, we can't use singletons
    ) -> Optional[Registration]:
        """Find the best-match registration, if any.

        Using the registry is a two-step process: lookup an implementation,
        then if needed, construct and return. This is the first part.
        """
        tr = self.registrations[kind]
        if allow_singletons:
            registrations = tr["singletons"] | tr["classes"]
        else:
            registrations = tr["classes"]

        # We will put possible matches into three piles: high/medium/low
        # precedence. Each pile is an ordered list based on registration
        # time (later registrations override earlier.)
        precedences: dict[str, list[Registration]] = dict(
            high=list(),
            medium=list(),
            low=list(),
        )
        for this_context, these_registrations in registrations.items():
            if this_context is IsNoneType and context_class is None:
                # This is the most basic case, test it first to bail out quickly.
                precedences["low"] = these_registrations
            elif this_context is context_class:
                precedences["high"] = these_registrations
            elif this_context is IsNoneType:
                precedences["low"] = these_registrations
            if this_context is not IsNoneType:
                # TODO mypy didn't like issubclass(context_class, this_context)
                if context_class and issubclass(
                    context_class, cast(type, this_context)
                ):
                    precedences["medium"] = these_registrations
            # Otherwise, filter it out and do nothing

        # Get the first match and return (is_singleton=True) or construct
        # and return (is_singleton = False)
        matches = precedences["high"] + precedences["medium"] + precedences["low"]

        # If we found a match, return it
        if matches:
            return matches[0]
        else:
            if self.parent:
                # Otherwise, go to parent
                return self.parent.get_best_match(
                    kind,
                    context_class=context_class,
                    allow_singletons=allow_singletons,
                )
            return None

    def get(  # noqa: C901
        self,
        kind: Type[T],
        context: Optional[Any] = None,
        **kwargs: Props,
    ) -> T:
        """Find an appropriate kind class and construct an implementation.

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

        # Use precedence etc. to get the best matching implementation.
        best_match = self.get_best_match(
            kind,
            context_class=context_class,
            # If props are passed in, we can't use singletons. So
            # allow_singletons when bool(kwargs) is false.
            allow_singletons=not bool(kwargs),
        )
        if best_match:
            if best_match.is_singleton:
                # TODO Now that ``.get()`` makes promises about typing, it makes
                #    registering a singleton for a "kind" a good bit harder.
                #    We'll just shut this up for now.
                return best_match.implementation  # type: ignore
            else:
                # Need to construct it
                instance: T = self.inject(best_match, props=kwargs)
                return instance

        # If we get to here, we didn't find anything, raise an error
        msg = f"No kind '{kind.__name__}' in registry"
        raise LookupError(msg)

    def register(
        self,
        implementation: T,
        *,
        kind: Optional[Type[T]] = None,
        context: Optional[Any] = None,
    ) -> None:
        """Use a LIFO list for all the possible implementations.

        Note that the implementation must be a subclass of the kind.
        """
        is_singleton = not isclass(implementation)

        registration = Registration(
            implementation=implementation,
            context=context,
            kind=kind,
            is_singleton=is_singleton,
        )

        # Let's decide what key to use to register this as.
        if kind is None:
            # Let's try to infer it from the subclass.
            if isclass(implementation):
                base_classes = getmro(implementation)[:-1]
                if len(base_classes) > 1:
                    # This registration is a class with a single base class
                    st = base_classes[1]
                else:
                    # Mimic the part below to finish this branch
                    st = implementation
            else:
                st = type(implementation) if is_singleton else implementation
        else:
            st = kind

        # Put this in the correct place of the registrations tree,
        # creating tree nodes as needed.

        s_or_c = "singletons" if is_singleton else "classes"
        registrations = self.registrations[st][s_or_c]  # type: ignore
        this_context = IsNoneType if context is None else context
        registrations[this_context].insert(0, registration)


class injectable:  # noqa
    """``venusian`` decorator to register an injectable factory ."""

    kind: Optional[
        Type[T]
    ] = None  # Give subclasses a chance to give default, e.g. view
    is_singleton: bool = False  # Decorator registers singletons.

    def __init__(
        self,
        kind: Optional[Type[T]] = None,
        *,
        context: Optional[Optional[Any]] = None,
    ):
        """Construct decorator that can register later with registry."""
        if kind:
            self.kind = kind
        self.context = context

    def __call__(self, wrapped: T) -> T:
        """Execute the decorator during venusian scan phase."""

        def callback(scanner: Scanner, name: str, cls: type) -> None:
            """Perform the work of actually putting in registry."""
            # Does this custom decorator want to register singletons? If
            # so, make an instance to use instead of decorated class target.
            target = cls() if self.is_singleton else cls
            registry = getattr(scanner, "registry")
            registry.register(
                implementation=target,
                kind=self.kind,
                context=self.context,
            )

        attach(wrapped, callback)
        return wrapped
