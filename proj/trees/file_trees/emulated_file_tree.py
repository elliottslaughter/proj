from dataclasses import dataclass
from typing import (
    Dict,
    Optional,
    Iterator,
    Mapping,
)
from ..file_tree import FileTree
from pathlib import PurePath

@dataclass(eq=True)
class EmulatedFileTree(FileTree):
    _m: Dict[PurePath, Optional[str]]

    def has_path(self, p: PurePath) -> bool:
        return p in self._m

    def has_dir(self, p: PurePath) -> bool:
        return self._m[p] is None

    def has_file(self, p: PurePath) -> bool:
        return self._m[p] is not None

    def ls_dir(self, p: PurePath) -> Iterator[PurePath]: 
        assert self.has_dir(p)
        for path in self._m:
            if path == (p / path.name):
                yield path

    def rename(self, src: PurePath, dst: PurePath) -> None:
        raise NotImplementedError()

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
        self._m[p] = None

    def get_file_contents(
        self,
        p: PurePath
    ) -> str:
        assert self.has_file(p)
        contents = self._m[p]
        assert contents is not None
        return contents

    def set_file_contents(
        self, 
        p: PurePath, 
        contents: str, 
        exist_ok: bool = False, 
        parents: bool = False,
    ) -> None:
        if not exist_ok:
            assert not self.has_file(p)
        if parents:
            self.mkdir(p.parent)
        self._m[p] = contents

    def rm_file(self, p: PurePath) -> None:
        assert self.has_file(p)
        del self._m[p]

    def restrict_to_subdir(self, p: PurePath) -> 'EmulatedFileTree':
        assert self.has_dir(p)
        return EmulatedFileTree({
            k.relative_to(p): v for k, v in self._m.items()
            if k.is_relative_to(p)
        })

    def with_extension(self, extension: str) -> Iterator[PurePath]:
        assert extension.startswith('.')
        for path in self._m:
            if path.name.endswith(extension):
                yield path

    def files(self) -> Iterator[PurePath]:
        for path in self._m:
            if self.has_file(path):
                yield path

    @staticmethod
    def from_map(m: Mapping[PurePath, Optional[str]]) -> 'EmulatedFileTree':
        expanded: Dict[PurePath, Optional[str]] = {}
        for p, contents in m.items():
            _p = PurePath(p)
            for parent in _p.parents:
                assert expanded.get(parent, None) is None
                expanded[parent] = None
            expanded[_p] = contents
        return EmulatedFileTree(expanded) 


