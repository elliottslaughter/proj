from ..path_tree import MutablePathTree
from typing import (
    Dict,
    Iterator,
    Mapping,
    Union,
)
from enum import (
    Enum,
    auto,
)
from dataclasses import dataclass
from pathlib import PurePath, Path
import os

class PathType(Enum):
    FILE = auto()
    DIR = auto()

@dataclass(eq=True)
class EmulatedPathTree(MutablePathTree):
    _paths: Dict[PurePath, PathType]

    def has_path(self, p: PurePath) -> bool:
        return p in self._paths

    def has_dir(self, p: PurePath) -> bool:
        return self._paths.get(p) == PathType.DIR

    def has_file(self, p: PurePath) -> bool:
        return self._paths.get(p) == PathType.FILE

    def ls_dir(self, p: PurePath) -> Iterator[PurePath]: 
        assert self.has_dir(p)
        for path in self._paths:
            if path == (p / path.name):
                yield path

    def restrict_to_subdir(self, p: PurePath) -> 'EmulatedPathTree':
        assert self.has_dir(p)
        return EmulatedPathTree({
            k.relative_to(p): v for k, v in self._paths.items()
            if k.is_relative_to(p)
        })

    def mkdir(
        self, 
        p: PurePath, 
        exist_ok: bool = False, 
        parents: bool = False,
    ) -> None:
        if not exist_ok:
            assert not self.has_dir(p)
        if parents:
            for parent in p.parents[::-1]:
                self.mkdir(parent, exist_ok=True, parents=False)
        self._paths[p] = PathType.DIR

    def rm_file(self, p: PurePath) -> None:
        assert self.has_file(p)
        del self._paths[p]

    def with_extension(self, extension: str) -> Iterator[PurePath]:
        assert extension.startswith('.')
        for path in self._paths:
            if path.name.endswith(extension):
                yield path

    def files(self) -> Iterator[PurePath]:
        for path in self._paths:
            if self.has_file(path):
                yield path

    def rename(self, src: PurePath, dst: PurePath) -> None:
        assert self.has_path(src)
        assert self.has_dir(dst.parent)
        assert not self.has_path(dst)
        self._paths[dst] = self._paths[src]
        del self._paths[dst]

    @staticmethod
    def from_map(m: Union[Mapping[PurePath, PathType]]) -> 'EmulatedPathTree':
        expanded: Dict[PurePath, PathType] = {}
        for p, path_type in m.items():
            for parent in p.parents:
                assert expanded.get(parent, PathType.DIR) == PathType.DIR, expanded.get(parent)
                expanded[parent] = PathType.DIR
            expanded[p] = path_type
        return EmulatedPathTree(expanded)

    @staticmethod
    def from_fs(base: Path) -> 'EmulatedPathTree':
        if base.is_file():
            return EmulatedPathTree.from_map({
                PurePath(''): PathType.FILE,
            })
        else:
            assert base.is_dir()
            path_map: Dict[PurePath, PathType] = {}
            for (dirpath, dirnames, filenames) in os.walk(base):
                _dirpath = PurePath(dirpath).relative_to(base)
                for fname in filenames:
                    path_map[_dirpath / fname] = PathType.FILE
                for dirname in dirnames:
                    path_map[_dirpath / dirname] = PathType.DIR
            return EmulatedPathTree.from_map(path_map)
