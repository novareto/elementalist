import typing as t
from dataclasses import dataclass, field
from prejudice.errors import ConstraintsErrors
from prejudice.types import Predicate
from prejudice.utils import resolve_constraints


V = t.TypeVar('V')
K = t.TypeVar('K', bound=t.Hashable)


@dataclass
class Element(t.Generic[K, V]):
    value: V
    key: K
    name: str = ''
    title: str = ''
    description: str = ''
    conditions: t.Tuple[Predicate] = field(default_factory=tuple)
    classifiers: t.FrozenSet[str] = field(default_factory=frozenset)
    metadata: t.Mapping[str, t.Any] = field(default_factory=dict)

    def __name__(self):
        return self.name

    def evaluate(self, *args, **kwargs) -> ConstraintsErrors | None:
        return resolve_constraints(self.conditions, self, *args, **kwargs)

    def __call__(self, *args, silence_errors=True, **kwargs):
        if not isinstance(self.value, t.Callable):
            raise ValueError(f'{self.value} is not callable.')
        if errors := self.evaluate(*args, **kwargs):
            if not silence_errors:
                raise errors
        else:
            return self.value(*args, **kwargs)
