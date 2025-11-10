from typing import (
    List,
    Union,
    Iterator,
)
from pathlib import PurePath
from ..path_tree import (
    TracedMutablePathTree,
    MutablePathTree,
    MoveTrace,
    MkDirTrace,
    RmFileTrace,
)

class MutableTracedPathTreeByWrapping(TracedMutablePathTree):
    _wrapped: MutablePathTree
    _trace: List[Union[
        MoveTrace, 
        MkDirTrace, 
        RmFileTrace,
    ]]

    def __init__(self, path_tree: MutablePathTree) -> None:
        self._wrapped = path_tree
        self._trace = list()

    def get_path_trace(self) -> List[Union[MoveTrace, MkDirTrace, RmFileTrace]]:
        return list(self._trace)

    def has_path(self, p: PurePath) -> bool:
        return self._wrapped.has_path(p=p)

    def has_dir(self, p: PurePath) -> bool:
        return self._wrapped.has_dir(p=p)

    def ls_dir(self, p: PurePath) -> Iterator[PurePath]: 
        return self._wrapped.ls_dir(p=p)

    def restrict_to_subdir(self, p: PurePath) -> 'MutableTracedPathTreeByWrapping':
        return MutableTracedPathTreeByWrapping(
            self._wrapped.restrict_to_subdir(p=p),
        )

    def has_file(self, p: PurePath) -> bool:
        return self.has_file(p=p)

    def with_extension(self, extension: str) -> Iterator[PurePath]:
        return self._wrapped.with_extension(extension=extension)

    def files(self) -> Iterator[PurePath]:
        return self._wrapped.files()

    def dirs(self) -> Iterator[PurePath]:
        return self._wrapped.dirs()


    def mkdir(
        self, 
        p: PurePath, 
        exist_ok: bool = False, 
        parents: bool = False,
    ) -> None:
        self._trace.append(
            MkDirTrace(
                path=p,
            )
        )
        self._wrapped.mkdir(
            p=p,
            exist_ok=exist_ok,
            parents=parents,
        )

    def rename(
        self,
        src: PurePath,
        dst: PurePath,
    ) -> None:
        self._trace.append(
            MoveTrace(
                src=src,
                dst=dst,
            )
        )
        self._wrapped.rename(
            src=src,
            dst=dst,
        )

    def rm_file(
        self,
        p: PurePath,
    ) -> None:
        self._trace.append(
            RmFileTrace(
                path=p,
            )
        )
        self._wrapped.rm_file(
            p=p,
        )
