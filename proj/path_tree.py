from dataclasses import dataclass
from typing import (
    Mapping,
    Dict,
)
from pathlib import (
    PurePath,
    Path,
)
import os

@dataclass(frozen=True)
class RelativePathTree:
    _paths: Mapping[PurePath, bool]

    def has_path(self, p: PurePath) -> bool:
        return p in self._paths

    def is_dir(self, p: PurePath) -> bool:
        return self._paths[p] is False

    def is_file(self, p: PurePath) -> bool:
        return self._paths[p] is True

    @staticmethod
    def from_map(m: Mapping[PurePath, bool]) -> 'RelativePathTree':
        expanded: Dict[PurePath, bool] = {}
        for p, is_file in m.items():
            for parent in p.parents:
                assert expanded.get(parent, False) is False, expanded.get(parent)
                expanded[parent] = False
            expanded[p] = is_file
        return RelativePathTree(expanded)

    @staticmethod
    def from_fs(base: Path) -> 'RelativePathTree':
        if base.is_file():
            return RelativePathTree.from_map({
                Path(''): True,
            })
        else:
            assert base.is_dir()
            path_map: Dict[PurePath, bool] = {}
            for (dirpath, dirnames, filenames) in os.walk(base):
                _dirpath = PurePath(dirpath).relative_to(base)
                for fname in filenames:
                    path_map[_dirpath / fname] = True
                for dirname in dirnames:
                    path_map[_dirpath / dirname] = False
            return RelativePathTree.from_map(path_map)

@dataclass(frozen=True)
class AbsolutePathTree:
    _root: PurePath
    _relative: RelativePathTree

    @staticmethod
    def from_map(root: PurePath, m: Mapping[PurePath, bool]) -> 'AbsolutePathTree':
        assert root.is_absolute()
        return AbsolutePathTree(
            root, 
            RelativePathTree.from_map(m),
        )

    @staticmethod
    def from_fs(base: Path) -> 'AbsolutePathTree':
        assert base.is_absolute()
        return AbsolutePathTree(base, RelativePathTree.from_fs(base))
