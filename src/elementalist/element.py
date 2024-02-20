import typing as t
from prejudice.errors import ConstraintsErrors
from prejudice.types import Predicate
from prejudice.utils import resolve_constraints
from pydantic import BaseModel, Field


V = t.TypeVar('V')
K = t.TypeVar('K', bound=t.Hashable)


class Element(BaseModel, t.Generic[K, V]):
    value: V
    key: K
    name: str = ''
    title: str = ''
    description: str = ''
    conditions: t.Tuple[Predicate, ...] = Field(default_factory=tuple)
    classifiers: t.FrozenSet[str] = Field(default_factory=frozenset)
    metadata: t.Mapping[str, t.Any] = Field(default_factory=dict)

    def __name__(self):
        return self.name

    def evaluate(self, *args, **kwargs) -> ConstraintsErrors | None:
        return resolve_constraints(self.conditions, self, *args, **kwargs)

    def conditional_call(self, *args, **kwargs):
        if not isinstance(self.value, t.Callable):
            raise ValueError(f'{self.value} is not callable.')
        if self.conditions:
            if errors := self.evaluate(*args, **kwargs):
                return None
        return self.value(*args, **kwargs)

    def secure_call(self, *args, **kwargs):
        if not isinstance(self.value, t.Callable):
            raise ValueError(f'{self.value} is not callable.')
        if self.conditions:
            if errors := self.evaluate(*args, **kwargs):
                raise errors
        return self.value(*args, **kwargs)
