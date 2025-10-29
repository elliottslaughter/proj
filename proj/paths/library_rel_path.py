from dataclasses import dataclass, field
from pathlib import PurePath
from typing import (
    Union,    
    Optional,
)
from .library import Library
from .repo_rel_path import RepoRelPath

@dataclass(frozen=True)
class LibraryRelPath:
    path: PurePath
    library: Optional[Library] = field(default=None)

    @staticmethod
    def from_str(s: str) -> 'LibraryRelPath':
        return LibraryRelPath(PurePath(s))

    def __truediv__(self, other: Union[str, PurePath]) -> 'LibraryRelPath':
        return LibraryRelPath(self.path / other, library=self.library)

    def to_repo_rel(self) -> 'RepoRelPath':
        assert self.library is not None
        return RepoRelPath(PurePath('lib') / self.library.name / self.path)
