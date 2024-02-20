import typing as t
from enum import Enum
from abc import ABC, abstractmethod
from plum import Signature
from .resolvers import T, Resolver, SignatureResolver
from .collections import E, Elements, ElementCollection, ElementMapping


DEFAULT = ""
Default = t.Literal[DEFAULT]


class Lookup(str, Enum):
    ALL = 'all'


class Registry(t.Generic[E], ABC):

    resolver: Resolver
    store: Elements[E]

    def __init__(self, resolver: Resolver, store: Elements[E]):
        self.resolver = resolver
        self.store = store

    @abstractmethod
    def match(self, target: T) -> t.Iterable[E]:
        ...

    def create(self, value, *args, **kwargs) -> E:
        return self.store.create(value, *args, **kwargs)

    def register(self, *args, **kwargs):
        def register_resolver(func):
            self.create(func, *args, **kwargs)
            return func
        return register_resolver

    def __or__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Unsupported merge between {self.__class__!r} "
                f"and {other.__class__!r}"
            )
        return self.__class__(
            resolver=self.resolver | other.resolver,
            store=self.store | other.store
        )


class SignatureRegistry(t.Generic[E], Registry[E]):

    resolver: SignatureResolver
    store: Elements[E]
    restrict: t.Set[Signature]

    def assert_valid(self, signature: Signature):
        if self.restrict:
            if not any((signature <= s) for s in self.restrict):
                raise AssertionError(
                    'Signature does not match restrictions.')

    def create(self,
               value: t.Any,
               discriminant: t.Iterable[t.Type],
               **kwargs):
        signature = Signature(*discriminant)
        self.assert_valid(signature)
        self.resolver.register(signature)
        return self.store.create(value, signature, **kwargs)

    def __or__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Unsupported merge between {self.__class__!r} "
                f"and {other.__class__!r}"
            )
        return self.__class__(
            resolver=self.resolver | other.resolver,
            store=self.store | other.store,
            restrict=self.restrict | other.restrict
        )


class CollectionRegistry(SignatureRegistry):

    def __init__(self, *,
                 resolver: SignatureResolver | None = None,
                 store: ElementMapping[Signature, E] | None = None,
                 restrict: t.Iterable[Signature] | None = None):

        if resolver is None:
            resolver = SignatureResolver()
        self.resolver = resolver

        if restrict is None:
            restrict = set()
        self.restrict = set(restrict)

        if store is None:
            store = ElementCollection()
        self.store = store

    def match(self, *args):
        found = []

        def sorting_key(handler):
            return handler.key

        found = [element for element in self.store
                 if element.key.match(args)]
        found.sort(key=sorting_key)
        return found


class MappingRegistry(SignatureRegistry):

    def __init__(self, *,
                 resolver: SignatureResolver | None = None,
                 store: ElementMapping[Signature, E] | None = None,
                 restrict: t.Iterable[Signature] | None = None):

        if resolver is None:
            resolver = SignatureResolver()
        self.resolver = resolver

        if restrict is None:
            restrict = set()
        self.restrict = set(restrict)

        if store is None:
            store = ElementMapping()
        self.store = store

    def lookup(self, *args) -> E:
        match = self.resolver.resolve(args)
        return self.store[match]

    def match(self, *args):
        found = []
        for signature, element in self.store.items():
            if signature.match(args):
                found.append(element)
        return sorted(found, key=lambda element: element.key)


class NamedElementRegistry(MappingRegistry):

    def create(self,
               value: t.Any,
               discriminant: t.Iterable[t.Type],
               name: str = DEFAULT,
               **kwargs):
        signature = Signature(
            *discriminant,
            t.Literal[name] | t.Literal[Lookup.ALL]
        )
        self.assert_valid(signature)
        self.resolver.register(signature)
        return self.store.create(value, signature, name=name, **kwargs)

    def get(self, *args, name: str = DEFAULT):
        return self.lookup(*args, name)

    def match(self, *args):
        elements = {}
        for element in super().match(*args, Lookup.ALL):
            if element.name not in elements:
                elements[element.name] = element
        return elements


class SpecificElementRegistry(MappingRegistry):

    def create(self,
               value: t.Any,
               discriminant: t.Iterable[t.Type],
               name: str = DEFAULT,
               **kwargs):
        signature = Signature(t.Literal[name], *discriminant)
        self.assert_valid(signature)
        self.resolver.register(signature)
        return self.store.create(value, signature, name=name, **kwargs)

    def get(self, *args, name: str = DEFAULT):
        return self.lookup(name, *args)
