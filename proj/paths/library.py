from dataclasses import dataclass, field
from .repo import Repo
from typing import Optional

@dataclass(frozen=True)
class Library:
    name: str
    repo: Optional[Repo] = field(default=None)
