import typing as t
from abc import ABC, abstractmethod
from collections import UserList, UserDict
from .element import K, V, Element


E = t.TypeVar('E', bound=Element)


class Elements(t.Generic[E], ABC):

    ElementType: t.Type[E] = Element

    @abstractmethod
    def add(self, element: E):
        pass

    def factory(self,
              value: T,
              key: K,
              name: str = '',
              title: str = '',
              description: str = '',
              conditions: t.Optional[t.Iterable[Predicate]] = None,
              classifiers: t.Optional[t.Iterable[str]] = None,
              **metadata: t.Any
              ):

        if classifiers is None:
            classifiers = ()

        if conditions is None:
            conditions = ()

        return self.ElementType(
            key=key,
            name=name,
            title=title,
            value=value,
            classifiers=frozenset(classifiers),
            conditions=tuple(conditions),
            metadata=metadata
        )

    def create(self, value, *args, **kwargs):
        element = self.factory(value, *args, **kwargs)
        self.add(element)
        return element

    def register(self, *args, **kwargs):
        def register_resolver(func):
            self.create(func, *args, **kwargs)
            return func
        return register_resolver


class ElementCollection(t.Generic[E], Elements[E], UserList):

    def add(self, element: E):
        self.append(element)

    def __or__(self, other):
        return self.__class__([*self, *other])


class ElementMapping(t.Generic[K, E], Elements[E], UserDict[K, E]):

    def add(self, element: E):
        self[element.key] = element
