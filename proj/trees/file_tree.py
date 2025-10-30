from pathlib import (
    PurePath,
)
from .path_tree import (
    PathTree,
    MutablePathTree,
)
import abc

class FileTree(PathTree):
    @abc.abstractmethod
    def get_file_contents(
        self,
        p: PurePath,
    ) -> str:
        ...

class MutableFileTree(MutablePathTree, FileTree):
    @abc.abstractmethod
    def set_file_contents(
        self, 
        p: PurePath, 
        contents: str, 
        exist_ok: bool = False, 
        parents: bool = False,
    ) -> None:
        ...

class FileTreeWithMtime(FileTree):
    @abc.abstractmethod
    def get_mtime(self, p: PurePath) -> float:
        ...

class MutableFileTreeWithMtime(MutableFileTree, FileTreeWithMtime):
    ...
