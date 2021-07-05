"""Type-oriented registry that start simple and finishes powerful."""
from __future__ import annotations

from abc import ABCMeta
from collections import defaultdict
from dataclasses import dataclass, field
from importlib import import_module
from types import ModuleType
from typing import Any, Optional, Type, TypeVar, Union

from venusian import Scanner

from .callers import caller_package
from .field_infos import get_field_infos, FieldInfos

PACKAGE = Optional[Union[ModuleType, str]]
Props = dict[str, Any]


@dataclass()
class Registration:
    """Collect registration and introspection info of a target."""

    slots = ("implementation", "servicetype", "context", "field_infos", "is_singleton")
    # TODO Andrey Since only services or xxx_singletons can be registered,
    #   shouldn't this be ``Type[Service]``?
    implementation: Union[Type[T], T]
    servicetype: Optional[Type[T]] = None
    context: Optional[type] = None
    field_infos: FieldInfos = field(default_factory=list)
    is_singleton: bool = False


class Service(metaclass=ABCMeta):
    """Type-oriented base class that supports looking up implementations."""

    @classmethod
    def select(
            cls: Type[T],
            registry: Registry,
            props: Optional[Props],
            context: Optional[Any] = None,
    ) -> Type[T]:
        """Default implementation selects based on context registration."""
        context_class = context.__class__
        try:
            return next(
                klass
                for klass in registry.get_implementations(cls)
                if getattr(klass, "__hopscotch_context__", None) is context_class
            )
        except StopIteration:
            # We couldn't find one matching this context, get the first
            # one for context=None.
            return next(
                klass
                for klass in registry.get_implementations(cls)
                if getattr(klass, "__hopscotch_context__", None) is None
            )


# TODO Andrey should this be bound to ``Service``? Or maybe just use
#   ``Type[Service]`` everywhere and eliminate this ``TypeVar``?
T = TypeVar("T")


def is_service_component(callable_: Any) -> bool:
    """Simplify checking if something is a 'service'."""
    try:
        return issubclass(callable_, Service)
    except TypeError:
        return False


def inject_callable(
        target: Type[T],
        props: Optional[Props] = None,
        registry: Optional[Registry] = None,
) -> T:
    """Construct target with or without a registry."""
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
        # Ask the registry to get the cached service info, creating
        # it if needed
        # TODO Paul When move to registry.registrations is complete,
        #   remove this and the method.
        service_info = registry.get_service_info(target)
        these_field_infos = service_info.field_infos
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
        elif registry and ft in registry.xxx_singletons:
            field_value = registry.xxx_singletons[ft]
        elif registry and ft is Registry:
            # Special rule: if you ask for the registry, you'll get it
            field_value = registry
        elif registry and is_service_component(ft):
            # TODO This implies that we can only inject something if it
            #  is a subclass of ``Service`` or a singleton. Make sure to
            #  state this in documentation.
            field_value = registry.get_service(ft)
        elif field_info.default_value is not None:
            field_value = field_info.default_value
        else:
            ql = target.__qualname__
            msg = f"Cannot inject {ft} on {ql}.{fn}"
            raise ValueError(msg)

        kwargs[fn] = field_value

    # Construct and return the class
    return target(**kwargs)  # type: ignore


class Registry:
    """Type-oriented registry with special features."""

    context: Optional[Any]
    parent: Optional[Registry]
    scanner: Scanner
    service_infos: dict[Type[T], Registration]
    services: dict[Type[T], list[Registration]]
    singletons: dict[Type[T], list[Registration]]

    def __init__(
            self,
            parent: Optional[Registry] = None,
            context: Optional[Any] = None,
    ):
        """Construct a registry that might have a context and be nested."""
        # TODO Andrey This should be ``list[Type[T]]`` to match
        #  ``get_implementations`` return type, but when I try, I get
        #  an unbound type problem. Or, even better, ``Type[Service]``?
        self.classes: dict[type, list[type]] = defaultdict(list)
        self.service_infos = {}
        self.services = defaultdict(list)
        self.singletons = defaultdict(list)
        # TODO Andrey Same thing here, not sure this is the correct
        #  type hint.
        self.xxx_singletons: dict[type, object] = {}
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

    def get_implementations(self, servicetype: Type[T]) -> list[Type[T]]:
        """Walk the registry hierarchy to find one with registered implementations."""
        classes = self.classes.get(servicetype)
        if classes is None:
            if self.parent is not None:
                return self.parent.get_implementations(servicetype)
            else:
                msg = f"No service '{servicetype.__name__}' in registry"
                raise LookupError(msg)

        return classes

    def inject(self, cls: Type[T], props: Optional[Props] = None) -> T:
        """Use injection to construct and return an instance."""
        return inject_callable(cls, props=props, registry=self)

    def get_service_info(self, target: Type[T]) -> Registration:
        """Return target's introspected service info, generating if needed.

        Hopscotch relies on information in the registration and in the
        introspection of a target. Rather than compute this on every
        lookup, it is done once and stored in the registry. This is done
        lazily, though, the first time it is asked for.
        """

        try:
            return self.service_infos[target]
        except KeyError:
            field_infos = get_field_infos(target)
            service_info = Registration(
                implementation=target,
                field_infos=field_infos,
            )
            self.service_infos[target] = service_info
            return service_info

    def get_service(
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

        # SINGLETONS: But *only* if this call passed in no props.
        if not kwargs and self.singletons:
            precedences: list[Optional[Registration]] = [None, None, None]
            for registration in self.singletons[servicetype]:
                # If context_class is None, then the only match will be a
                # singleton registered for None
                singleton_context = registration.context
                if context_class is None:
                    if singleton_context is None:
                        # Low precedence
                        precedences[2] = registration
                    else:
                        continue
                if singleton_context is context_class:
                    # Highest precedence, this singleton was registered for
                    # the same class
                    precedences[0] = registration
                    continue
                if singleton_context and issubclass(context_class, singleton_context):
                    # Second highest precedence,
                    precedences[1] = registration
                    continue
                if singleton_context is None:
                    precedences[2] = registration
                    continue
            # Return best-matching singleton, if found
            for precedence in precedences:
                if precedence is not None:
                    return precedence.implementation

        # SERVICES: Similar logic, but give ``select`` a chance to
        # narrow *after* the generic narrowing for context.
        precedences: list[Optional[Registration]] = [None, None, None]
        for registration in self.services[servicetype]:
            service_context = registration.context
            if context_class is None:
                if service_context is None:
                    # Low precedence
                    precedences[2] = registration
                else:
                    continue
            if service_context is context_class:
                # Highest precedence, this service was registered for
                # the same class
                precedences[0] = registration
                continue
            if service_context and issubclass(context_class, service_context):
                # Second highest precedence,
                precedences[1] = registration
                continue
            if service_context is None:
                precedences[2] = registration
                continue

        # Return best-matching singleton, if found
        for precedence in precedences:
            if precedence is not None:
                # TODO Somewhere in here, let ``Service.select`` get involved
                #   to narrow the candidates, instead of just taking the first
                #   one, which is a mistake anyway.
                klass = precedence.implementation
                instance = self.inject(klass, props=kwargs)
                return instance

        # Try with the parents
        if self.parent is not None:
            return self.parent.get_service(servicetype, context, **kwargs)

        # If we get to here, we didn't find anything, raise an error
        msg = f"No service '{servicetype.__name__}' in registry"
        raise LookupError(msg)

    def register_singleton(
            self,
            instance: T,
            *,
            servicetype: Optional[Type[T]] = None,
            context: Optional[Any] = None,
    ) -> None:
        """Register an instance as the lookup value for a type."""
        registration = Registration(
            implementation=instance,
            context=context,
            servicetype=servicetype,
            is_singleton=True,
        )
        if servicetype is None:
            servicetype = type(instance)
        self.xxx_singletons[servicetype] = instance

        self.singletons[servicetype].append(registration)

    # TODO Andrey if we make ``servicetype`` required, can we then "enforce" that
    #   the implementation "is a kind of" the servicetype? And thus, bring back
    #   registering non-Service?
    def register_service(
            self,
            implementation: Type[T],
            *,
            servicetype: Optional[Type[T]] = None,
            context: Optional[Any] = None,
    ) -> None:
        """Use a LIFO list for all the possible implementations.

        Note that the implementation must be a subclass of the servicetype.
        """
        registration = Registration(
            implementation=implementation,
            context=context,
            servicetype=servicetype,
        )

        if servicetype is None:
            servicetype = implementation
        self.services[servicetype].append(registration)
        # We store the registry_context registration info on the implementation
        # apart from "predicates", as it is built-in
        # setattr(implementation, "__hopscotch_context__", context)

        self.classes[servicetype].insert(0, implementation)
