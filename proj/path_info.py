from dataclasses import dataclass
from pathlib import Path
from enum import Enum, auto
from .utils import (
    map_optional,
)
from typing import (
    Optional,
)
# from .config_file import (
#     get_nongenerated_public_header_info,
#     get_private_header_info,
#     get_nongenerated_include_path,
#     get_generated_include_path,
#     try_get_generated_header_path,
#     try_get_nongenerated_header_path,
#     get_nongenerated_source_path,
#     get_test_source_path,
#     get_benchmark_source_path,
#     get_toml_path,
#     get_generated_source_path,
# )
from .json import (
    Json,
)

@dataclass(frozen=True, order=True)
class HeaderInfo:
    path: Path
    ifndef: str

    def json(self) -> Json:
        return {
            "path": str(self.path),
            "ifndef": self.ifndef,
        }

class PathRole(Enum):
    PUBLIC_HEADER = auto()
    PRIVATE_HEADER = auto()
    SOURCE = auto()
    TEST = auto()
    BENCHMARK = auto()
    TOML = auto()

@dataclass(frozen=True, order=True)
class PathInfo:
    include: Path
    generated_include: Path
    public_header: HeaderInfo
    private_header: HeaderInfo
    generated_header: Optional[Path]
    generated_source: Path
    header: Optional[Path]
    source: Path
    test_source: Optional[Path]
    benchmark_source: Optional[Path]
    toml_path: Optional[Path]

    def json(self) -> Json:
        return {
            "include": str(self.include),
            "generated_include": str(self.generated_include),
            "public_header": self.public_header.json(),
            "private_header": self.private_header.json(),
            "header": map_optional(self.header, str),
            "generated_header": map_optional(self.generated_header, str),
            "source": str(self.source),
            "generated_source": str(self.generated_source),
            "test_source": map_optional(self.test_source, str),
            "benchmark_source": map_optional(self.benchmark_source, str),
            "toml_path": map_optional(self.toml_path, str),
        }

    def path_for_role(self, role: PathRole) -> Optional[Path]:
        if role == PathRole.PUBLIC_HEADER:
            return self.public_header.path
        elif role == PathRole.PRIVATE_HEADER:
            return self.private_header.path
        elif role == PathRole.SOURCE:
            return self.source
        elif role == PathRole.TEST:
            return self.test_source
        elif role == PathRole.BENCHMARK:
            return self.benchmark_source
        elif role == PathRole.TOML:
            return self.toml_path
        else:
            raise ValueError(f'Unknown PathRole {role!r}')


def get_path_role(path_info: PathInfo, p: Path) -> PathRole:
    if p == path_info.public_header.path:
        return PathRole.PUBLIC_HEADER
    elif p == path_info.private_header.path:
        return PathRole.PRIVATE_HEADER
    elif p == path_info.source:
        return PathRole.SOURCE
    elif path_info.test_source is not None and p == path_info.test_source:
        return PathRole.TEST
    elif path_info.benchmark_source is not None and p == path_info.benchmark_source:
        return PathRole.BENCHMARK
    elif path_info.toml_path is not None and p == path_info.toml_path:
        return PathRole.TOML
    else:
        raise ValueError(f'Could not find role for path {p!r}')

def get_path_info(p: Path) -> PathInfo:
    assert False
#     public_header_info = get_nongenerated_public_header_info(p)
#     private_header_info = get_private_header_info(p)
#     return PathInfo(
#         include=get_nongenerated_include_path(p),
#         generated_include=get_generated_include_path(p),
#         public_header=public_header_info,
#         private_header=private_header_info,
#         generated_header=try_get_generated_header_path(p),
#         header=try_get_nongenerated_header_path(p),
#         source=get_nongenerated_source_path(p),
#         generated_source=get_generated_source_path(p),
#         test_source=get_test_source_path(p),
#         benchmark_source=get_benchmark_source_path(p),
#         toml_path=get_toml_path(p),
#     )
#
