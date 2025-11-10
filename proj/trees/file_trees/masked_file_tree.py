from typing import (
    Iterator,
)
from ..file_tree import (
    FileTree,
    PathTree,
)
from pathlib import PurePath

class MaskedFileTree(FileTree):
    _path_tree: PathTree
    _file_tree: FileTree

    def __init__(
        self,
        path_tree: PathTree,
        file_tree: FileTree,
    ) -> None:
        self._path_tree = path_tree
        self._file_tree = file_tree

    def has_path(self, p: PurePath) -> bool:
        return self._path_tree.has_path(p)

    def has_dir(self, p: PurePath) -> bool:
        return self._path_tree.has_dir(p)

    def ls_dir(self, p: PurePath) -> Iterator[PurePath]: 
        return self._path_tree.ls_dir(p)

    def restrict_to_subdir(self, p: PurePath) -> 'MaskedFileTree':
        return MaskedFileTree(
            path_tree=self._path_tree.restrict_to_subdir(p),
            file_tree=self._file_tree.restrict_to_subdir(p),
        )

    def has_file(self, p: PurePath) -> bool:
        return self._path_tree.has_file(p)

    def with_extension(self, extension: str) -> Iterator[PurePath]:
        return self._path_tree.with_extension(extension)

    def files(self) -> Iterator[PurePath]:
        return self._path_tree.files()

    def dirs(self) -> Iterator[PurePath]:
        return self._path_tree.dirs()

    def get_file_contents(
        self,
        p: PurePath,
    ) -> str:
        assert self.has_path(p)
        return self._file_tree.get_file_contents(p)
