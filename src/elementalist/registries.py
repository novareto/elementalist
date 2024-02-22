import typing as t
from enum import Enum
from abc import ABC, abstractmethod
from plum import Signature
from .resolvers import T, Resolver, SignatureResolver
from .element import Element
from .collections import E, Elements, ElementCollection, ElementMapping


DEFAULT = ""
Default = t.Literal[DEFAULT]


class Lookup(str, Enum):
    ALL = 'all'


def base_sorter(element):
    return element.key


class SignatureMapping(ElementMapping[Signature, E]):

    def __init__(self, *args, **kwargs):
        self.resolver: Resolver = SignatureResolver()
        super().__init__(*args, **kwargs)

    def create(self,
               value: t.Any,
               discriminant: t.Iterable[t.Type],
               name: str = DEFAULT,
               **kwargs):
        signature = Signature(
            *discriminant,
            t.Literal[name] | t.Literal[Lookup.ALL]
        )
        return super().create(value, signature, name=name, **kwargs)

    def __setitem__(self, signature: Signature, element: Element):
        self.resolver.register(element.key)
        super().__setitem__(signature, element)

    def _match(self, *args, sorter = base_sorter):
        found = []
        for signature, element in self.items():
            if signature.match(args):
                found.append(element)
        return sorted(found, key=sorter)

    def match(self, *args, name: str | Lookup, sorter = base_sorter):
        return self._match(*args, name, sorter=sorter)

    def match_grouped(self, *args, sorter = base_sorter):
        elements = {}
        for e in self._match(*args, Lookup.ALL, sorter=sorter):
            if e.name not in elements:
                elements[e.name] = e
        return elements

    def lookup(self, *args, name: str = DEFAULT) -> E:
        match = self.resolver.resolve((*args, name))
        return self[match]


class SignatureCollection(ElementCollection[E]):

    def __init__(self, *args, **kwargs):
        self.resolver: Resolver = SignatureResolver()
        super().__init__(*args, **kwargs)

    def create(self,
               value: t.Any,
               discriminant: t.Iterable[t.Type],
               name: str = DEFAULT,
               **kwargs):
        signature = Signature(*discriminant)
        return super().create(value, signature, name=name, **kwargs)

    def match(self, *args, sorter = base_sorter):
        found = [element for element in self if element.key.match(args)]
        found.sort(key=base_sorter)
        return found
