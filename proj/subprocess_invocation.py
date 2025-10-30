from pathlib import Path
from typing import (
    Sequence,
    Any,
    Dict,
    Optional,
    Mapping,
    Union,
    TextIO,
)
from dataclasses import dataclass, field
import subprocess

@dataclass(frozen=True)
class SubprocessInvocation:
    cmd: Sequence[str]
    cwd: Optional[Path] = field(default=None)
    stdout: Optional[Union[int, TextIO]] = field(default=None)
    stderr: Optional[Union[int, TextIO]] = field(default=None)
    env: Optional[Mapping[str, str]] = field(default=None)

    def check_call(self) -> None:
        kwargs: Dict[str, Any] = {}
        if self.cwd is not None:
            kwargs['cwd'] = self.cwd
        if self.stdout is not None:
            kwargs['stdout'] = self.stdout
        if self.stderr is not None:
            kwargs['stderr'] = self.stderr
        if self.env is not None:
            kwargs['env'] = self.env

        subprocess.check_call(self.cmd, **kwargs)
