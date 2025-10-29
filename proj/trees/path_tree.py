from typing import (
    Iterator,
    Self,
)
from pathlib import (
    PurePath,
)
import abc

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
    def restrict_to_subdir(self, p: PurePath) -> Self:
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

class MutablePathTree(PathTree):
    @abc.abstractmethod
    def mkdir(
        self, 
        p: PurePath, 
        exist_ok: bool = False, 
        parents: bool = False,
    ) -> None:
        ...

    @abc.abstractmethod
    def rename(self, src: PurePath, dst: PurePath) -> None:
        ...

    @abc.abstractmethod
    def rm_file(self, p: PurePath) -> None:
        ...


