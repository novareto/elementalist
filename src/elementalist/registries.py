import typing as t
from enum import Enum
from abc import ABC, abstractmethod
from plum import Signature
from .resolvers import T, Resolver, SignatureResolver, ComponentRegistry
from .collections import E, Elements, ElementCollection, ElementMapping
from zope.interface import Interface


DEFAULT = ""
Default = t.Literal[DEFAULT]


class Lookup(str, Enum):
    ALL = 'all'


class Registry(ElementCollection[E]):

    resolver: ComponentRegistry

    class resolve_to(Interface):
        pass

    def __init__(self):
        self.resolver = ComponentRegistry()
        super().__init__(self)

    def add(self, item: E):
        try:
            self.resolver.register(
                item.key, self.resolve_to, item.name, item
            )
        except:
            import pdb
            pdb.set_trace()
            print('')

        super().add(item)

    def match(self, *args):
        return self.resolver.lookup_all(args, self.resolve_to)

    def match_as_dict(self, *args):
        return dict(self.match(*args))

    def lookup(self, *args, name=''):
        return self.resolver.lookup(args, self.resolve_to, name)


class CollectionRegistry(ElementCollection[E]):

    resolver: ComponentRegistry

    class resolve_to(Interface):
        pass

    def __init__(self, *args, sorter=None):
        self.resolver = ComponentRegistry()
        self._sorter = sorter
        super().__init__(*args)

    def add(self, item: E):
        self.resolver.subscribe(
            item.key, self.resolve_to, item
        )
        super().add(item)

    def match(self, *args):
        found = list(self.resolver.subscriptions(args, self.resolve_to))
        if self._sorter is not None:
            found.sort(key=self._sorter)
        return found

    def notifications(self, *args):
        for handler in self.match(*args):
            yield handler(*args)

    def notify(self, *args):
        return list(self.notifications(*args))

    def __or__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                '{other!r} needs to be of type {self.__class__}.')
        return self.__class__(
            [*self, *other], sorter=other._sorter or self._sorter)
