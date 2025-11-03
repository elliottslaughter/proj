from pathlib import (
    PurePath,
)
from .path_tree import (
    PathTree,
    MutablePathTree,
    TracedMutablePathTree,
    MoveTrace,
    MkDirTrace,
    RmFileTrace,
)
import abc
from dataclasses import dataclass
from typing import (
    Sequence,
    Union,
)

class FileTree(PathTree):
    @abc.abstractmethod
    def get_file_contents(
        self,
        p: PurePath,
    ) -> str:
        ...

@dataclass(frozen=True)
class ModifyFileTrace:
    path: PurePath
    diff: str

@dataclass(frozen=True)
class CreateFileTrace:
    path: PurePath
    contents: str

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

class TracedMutableFileTree(MutableFileTree, TracedMutablePathTree):
    @abc.abstractmethod
    def get_file_trace(self) -> Sequence[Union[
        MoveTrace,
        MkDirTrace,
        RmFileTrace,
        CreateFileTrace,
        ModifyFileTrace,
    ]]:
        ...

class FileTreeWithMtime(FileTree):
    @abc.abstractmethod
    def get_mtime(self, p: PurePath) -> float:
        ...

class MutableFileTreeWithMtime(MutableFileTree, FileTreeWithMtime):
    ...
