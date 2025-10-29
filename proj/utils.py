from typing import (
    TypeVar,
    Optional,
    Callable,
    Collection,
    FrozenSet,
    Iterable,
    Iterator,
)
from functools import reduce
from pathlib import PurePath

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")


def concatmap(c: Iterable[T1], f: Callable[[T1], Iterable[T2]]) -> Iterable[T2]:
    for e in c:
        f_result = f(e)
        yield from f_result


def filtermap(c: Iterable[T1], f: Callable[[T1], Optional[T2]]) -> Iterable[T2]:
    for e in c:
        f_result = f(e)
        if f_result is None:
            continue
        yield f_result


def union_all(c: Iterable[FrozenSet[T]]) -> FrozenSet[T]:
    return reduce(lambda accum, x: accum.union(x), c, frozenset())


def get_only(c: Collection[T]) -> T:
    assert len(c) == 1
    return next(iter(c))


def require_nonnull(x: Optional[T]) -> T:
    assert x is not None
    return x


def map_optional(x: Optional[T1], f: Callable[[T1], T2]) -> Optional[T2]:
    if x is None:
        return x
    else:
        return f(x)

def common_ancestors(lhs: PurePath, rhs: PurePath) -> Iterator[PurePath]:
    for l, r in zip(lhs.parents[::-1], rhs.parents[::-1]):
        if l == r:
            yield l
        else:
            break

def nearest_common_ancestor(lhs: PurePath, rhs: PurePath) -> PurePath:
    for anc in common_ancestors(lhs, rhs):
        pass
    assert isinstance(anc, PurePath)
    return anc


def num_true(c: Iterable[bool]) -> int:
    return sum(int(b) for b in c)
