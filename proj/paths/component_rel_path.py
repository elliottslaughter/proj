from dataclasses import dataclass, field
from pathlib import PurePath
from typing import (
    Union,    
    Optional,
)
from .component import Component
from .repo_rel_path import RepoRelPath

@dataclass(frozen=True)
class ComponentRelPath:
    path: PurePath
    component: Optional[Component] = field(default=None)

    @staticmethod
    def from_str(s: str) -> 'ComponentRelPath':
        return ComponentRelPath(PurePath(s))

    def __truediv__(self, other: Union[str, PurePath]) -> 'ComponentRelPath':
        return ComponentRelPath(self.path / other, component=self.component)
