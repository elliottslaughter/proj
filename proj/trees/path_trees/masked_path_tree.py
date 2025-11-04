from typing import (
    Iterable,
    FrozenSet,
    Iterator,
)
from pathlib import PurePath
from ..path_tree import (
    PathTree,
)
from proj.utils import saturating_relative_to

class MaskedPathTree(PathTree):
    _wrapped: PathTree
    _mask: FrozenSet[PurePath]

    def __init__(self, path_tree: PathTree, to_hide: Iterable[PurePath]) -> None:
        self._wrapped = path_tree
        self._mask = frozenset(to_hide)

    @property
    def masked_out(self) -> FrozenSet[PurePath]:
        return self._mask

    def _is_masked(self, p: PurePath) -> bool:
        for _p in self._mask:
            if p.is_relative_to(_p):
                return True
        return False

    def _filter_masked(self, i: Iterable[PurePath]) -> Iterator[PurePath]:
        for p in i:
            if not self._is_masked(p):
                yield p 

    def has_path(self, p: PurePath) -> bool:
        if self._is_masked(p):
            return False
        return self._wrapped.has_path(p=p)

    def has_dir(self, p: PurePath) -> bool:
        if self._is_masked(p):
            return False
        return self._wrapped.has_dir(p=p)

    def ls_dir(self, p: PurePath) -> Iterator[PurePath]: 
        return self._filter_masked(self._wrapped.ls_dir(p=p))

    def restrict_to_subdir(self, p: PurePath) -> 'MaskedPathTree':
        return MaskedPathTree(
            path_tree=self._wrapped.restrict_to_subdir(p),
            to_hide=[
                rel for _p in self._mask if (rel := saturating_relative_to(_p, p)) is not None
            ],
        )

    def has_file(self, p: PurePath) -> bool:
        if self._is_masked(p):
            return False
        return self.has_file(p=p)

    def with_extension(self, extension: str) -> Iterator[PurePath]:
        return self._filter_masked(self._wrapped.with_extension(extension=extension))

    def files(self) -> Iterator[PurePath]:
        return self._filter_masked(self._wrapped.files())

    def dirs(self) -> Iterator[PurePath]:
        return self._filter_masked(self._wrapped.dirs())

    def __str__(self) -> str:
        return f'MaskedPathTree(_wrapped={self._wrapped}, _mask={self._mask})'
