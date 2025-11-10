from dataclasses import dataclass, field
from .repo import Repo
from typing import Optional
from .component_type import ComponentType

@dataclass(frozen=True)
class Component:
    name: str
    component_type: Optional[ComponentType]
    repo: Optional[Repo] = field(default=None)

    def __str__(self) -> str:
        if self.repo is None:
            return f'?:{self.name}'
        else:
            return f'{self.repo}:{self.name}'

    @staticmethod
    def library(name: str, repo: Optional[Repo] = None) -> 'Component':
        return Component(
            name=name,
            component_type=ComponentType.LIBRARY,
            repo=repo,
        )

    @staticmethod
    def executable(name: str, repo: Optional[Repo] = None) -> 'Component':
        return Component(
            name=name,
            component_type=ComponentType.EXECUTABLE,
            repo=repo,
        )

    @staticmethod
    def unknown(name: str, repo: Optional[Repo] = None) -> 'Component':
        return Component(
            name=name,
            component_type=None,
            repo=repo,
        )
