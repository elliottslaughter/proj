from dataclasses import dataclass
from pathlib import PurePath

@dataclass(frozen=True)
class Repo:
    path: PurePath
