from dataclasses import dataclass
from typing import (
    Mapping,
    Dict,
    Iterator,
    Union,
)
from pathlib import (
    PurePath,
    Path,
)
import os
from enum import (
    Enum,
    auto,
)
from .paths import (
    RepoRelPath,
    AbsolutePath,
    Repo,
)
import abc

class PathType(Enum):
    FILE = auto()
    DIR = auto()

class PathTree(abc.ABC): 
    @abc.abstractmethod
    def has_path(self, p: PurePath) -> bool:
        ...

    @abc.abstractmethod
    def has_dir(self, p: PurePath) -> bool:
        ...

    @abc.abstractmethod
    def ls_dir(self, p: PurePath) -> Iterator[PurePath]: 
        ...

    @abc.abstractmethod
    def restrict_to_subdir(self, p: PurePath) -> 'PathTree':
        ...

    @abc.abstractmethod
    def has_file(self, p: PurePath) -> bool:
        ...

    @abc.abstractmethod
    def with_extension(self, extension: str) -> Iterator[PurePath]:
        ...

    @abc.abstractmethod
    def files(self) -> Iterator[PurePath]:
        ...

@dataclass(frozen=True)
class EmulatedPathTree(PathTree):
    _paths: Mapping[PurePath, PathType]

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

    def with_extension(self, extension: str) -> Iterator[PurePath]:
        assert extension.startswith('.')
        for path in self._paths:
            if path.name.endswith(extension):
                yield path

    def files(self) -> Iterator[PurePath]:
        for path in self._paths:
            if self.has_file(path):
                yield path

    @staticmethod
    def from_map(m: Union[Mapping[str, PathType], Mapping[PurePath, PathType]]) -> 'PathTree':
        expanded: Dict[PurePath, PathType] = {}
        for p, path_type in m.items():
            _p = PurePath(p)
            for parent in _p.parents:
                assert expanded.get(parent, PathType.DIR) == PathType.DIR, expanded.get(parent)
                expanded[parent] = PathType.DIR
            expanded[_p] = path_type
        return EmulatedPathTree(expanded)

    @staticmethod
    def from_fs(base: Path) -> 'PathTree':
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

@dataclass(frozen=True)
class FilesystemPathTree(PathTree):
    _root: AbsolutePath

    def has_path(self, p: PurePath) -> bool:
        return (self._root / p).raw.exists()

    def has_dir(self, p: PurePath) -> bool:
        return (self._root / p).raw.is_dir()

    def has_file(self, p: PurePath) -> bool:
        return (self._root / p) .raw.is_file()

    def with_extension(self, extension: str) -> Iterator[PurePath]:
        assert extension.startswith('.')

        def has_extension(p: PurePath) -> bool:
            return p.name.endswith(extension)

        yield from filter(has_extension, self.files())

    def ls_dir(self, p: PurePath) -> Iterator[PurePath]: 
        yield from Path(self._root.raw / p).iterdir()

    def restrict_to_subdir(self, p: PurePath) -> 'FilesystemPathTree':
        assert self.has_dir(p)
        return FilesystemPathTree(self._root / p)

    def files(self) -> Iterator[PurePath]:
        base = self._root.raw

        for (dirpath, dirnames, filenames) in os.walk(base):
            _dirpath = PurePath(dirpath).relative_to(base)
            for fname in filenames:
                yield (_dirpath / fname)


def is_repo_path_tree(path_tree: PathTree) -> bool:
    return path_tree.has_file(PurePath('.proj.toml'))

def is_library_path_tree(path_tree: PathTree) -> bool:
    return all([
        path_tree.has_dir(PurePath('include')),
        path_tree.has_dir(PurePath('src')),
        path_tree.has_file(PurePath('CMakeLists.txt')),
    ])

@dataclass(frozen=True)
class RepoPathTree:
    _path_tree: PathTree

    def __post_init__(self) -> None:
        assert is_repo_path_tree(self._path_tree)

    def has_path(self, p: RepoRelPath) -> bool:
        return self._path_tree.has_path(p.raw)

    def has_dir(self, p: RepoRelPath) -> bool:
        return self._path_tree.has_dir(p.raw)

    def has_file(self, p: RepoRelPath) -> bool:
        return self._path_tree.has_file(p.raw)

    def with_extension(self, extension: str) -> Iterator[RepoRelPath]:
        for p in self._path_tree.with_extension(extension):
            yield RepoRelPath(p)

    @staticmethod
    def for_repo(repo: Repo) -> 'RepoPathTree':
        return RepoPathTree(FilesystemPathTree(repo.abs_path))
