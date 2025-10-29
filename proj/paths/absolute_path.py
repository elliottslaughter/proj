from io import TextIOWrapper
from pathlib import (
    PurePath, 
    Path,
)
import os
from typing import Union

class AbsolutePurePath:
    _raw: PurePath

    def __init__(self, p: Union[Path, str]) -> None:
        self._raw = PurePath(p)
        assert self._raw.is_absolute()

    @property
    def raw(self) -> PurePath:
        return self._raw

class AbsolutePath:
    _raw: Path

    def __init__(self, p: Union[AbsolutePurePath, Path, PurePath, str]) -> None:
        if isinstance(p, AbsolutePurePath):
            self._raw = Path(p._raw)
        else:
            self._raw = Path(p)

        assert self._raw.is_absolute()

    @property
    def raw(self) -> Path:
        return self._raw

    def exists(self) -> bool:
        return self._raw.exists()

    def is_file(self) -> bool:
        return self._raw.is_file()

    def is_dir(self) -> bool:
        return self._raw.is_dir()

    @property
    def parent(self) -> 'AbsolutePath':
        return AbsolutePath(self._raw.parent)

    def stat(self) -> os.stat_result:
        return self._raw.stat()

    def mkdir(self, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        self._raw.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)

    def open(self) -> TextIOWrapper:
        return self._raw.open('w')

    def __str__(self) -> str:
        return str(self._raw)

    def __truediv__(self, other: Union[str, PurePath]) -> 'AbsolutePath':
        return AbsolutePath(self._raw / other)
