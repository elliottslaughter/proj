from dataclasses import dataclass, field
from .repo import Repo
from typing import Optional

@dataclass(frozen=True)
class Library:
    name: str
    repo: Optional[Repo] = field(default=None)

    def __str__(self) -> str:
        if self.repo is None:
            return f'?:{self.name}'
        else:
            return f'{self.repo}:{self.name}'

