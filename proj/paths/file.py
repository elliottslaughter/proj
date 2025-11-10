from dataclasses import dataclass
from .role_in_group import RoleInGroup
from typing import TYPE_CHECKING
from .repo import Repo

if TYPE_CHECKING:
    from .file_group import FileGroup

@dataclass(frozen=True)
class File:
    group: 'FileGroup'
    role: RoleInGroup

    @property
    def repo(self) -> Repo:
        assert self.group.component is not None
        assert self.group.component.repo is not None
        return self.group.component.repo

    def __str__(self) -> str:
        return f'{self.group}:<{self.role.shortname}>'
