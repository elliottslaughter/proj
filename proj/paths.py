from pathlib import (
    PurePath, 
    Path,
)
from dataclasses import dataclass
from enum import (
    Enum,
    auto,
)
from typing import (
    Union,
    Iterator,
    List,
    Sequence,
)
from .absolute_path import AbsolutePath
from functools import total_ordering

@dataclass(frozen=True)
class Repo:
    raw: PurePath

    def __post_init__(self): 
        assert self.raw.is_absolute()

    @property
    def abs_path(self) -> AbsolutePath:
        return AbsolutePath(self.raw)
        
    def make_rel_path(self, p: AbsolutePath) -> 'RepoRelPath':
        return RepoRelPath(p.raw.relative_to(self.raw))

    def rglob(self, pattern: str) -> Iterator['RepoRelPath']:
        for found in Path(self.raw).rglob(pattern):
            yield RepoRelPath(found)

@total_ordering
class RepoRelPath:
    _raw: PurePath

    def __init__(self, p: Union[str, PurePath]) -> None:
        self._raw = PurePath(p)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RepoRelPath):
            return self._raw == other._raw
        else:
            return False

    def __lt__(self, other: object) -> bool:
        if isinstance(other, RepoRelPath):
            return self._raw < other._raw
        else:
            return False

    def __hash__(self) -> int:
        return hash((type(self).__name__, self._raw))

    @property
    def raw(self) -> PurePath:
        return self._raw

    def to_absolute(self, repo: Repo) -> 'AbsolutePath':
        return AbsolutePath(repo.raw / self.raw)

    def is_relative_to(self, other: 'RepoRelPath') -> bool:
        return self._raw.is_relative_to(other._raw)

    def __truediv__(self, other: Union[str, PurePath]) -> 'RepoRelPath':
        return RepoRelPath(self._raw / other)

    @property
    def name(self) -> str:
        return self._raw.name
    
    @property
    def parents(self) -> Sequence['RepoRelPath']:
        return [RepoRelPath(p) for p in self._raw.parents]
    
    @property
    def suffixes(self) -> List[str]:
        return self._raw.suffixes

def get_repo_rel_path(repo: Repo, p: PurePath) -> 'RepoRelPath':
    assert p.is_absolute()

    return RepoRelPath(p.relative_to(repo.raw))

class PathRole(Enum):
    PUBLIC_HEADER = auto()
    SOURCE = auto()
    TEST = auto()
    BENCHMARK = auto()
    STRUCT_TOML = auto()
    ENUM_TOML = auto()
    VARIANT_TOML = auto()
    GENERATED_HEADER = auto()
    GENERATED_SOURCE = auto()

    @property
    def shortname(self) -> str:
        return {
            PathRole.PUBLIC_HEADER: 'hdr',
            PathRole.SOURCE: 'src',
            PathRole.TEST: 'tst',
            PathRole.BENCHMARK: 'bmk',
            PathRole.STRUCT_TOML: 'struct',
            PathRole.ENUM_TOML: 'enum',
            PathRole.VARIANT_TOML: 'variant',
            PathRole.GENERATED_SOURCE: 'gensrc',
            PathRole.GENERATED_HEADER: 'genhdr',
        }[self]

@dataclass(frozen=True)
class FileGroup:
    group_path: PurePath

    @property
    def public_header(self) -> 'File':
        return File(self, PathRole.PUBLIC_HEADER)

    @property
    def source(self) -> 'File':
        return File(self, PathRole.SOURCE)

    @property
    def test(self) -> 'File':
        return File(self, PathRole.TEST)

    @property
    def benchmark(self) -> 'File':
        return File(self, PathRole.BENCHMARK)

    @property
    def generated_header(self) -> 'File':
        return File(self, PathRole.GENERATED_HEADER)

    @property
    def generated_source(self) -> 'File':
        return File(self, PathRole.GENERATED_HEADER)

    @property
    def struct_toml(self) -> 'File':
        return File(self, PathRole.STRUCT_TOML)

    @property
    def variant_toml(self) -> 'File':
        return File(self, PathRole.VARIANT_TOML)

    @property
    def enum_toml(self) -> 'File':
        return File(self, PathRole.ENUM_TOML)


@dataclass(frozen=True)
class File:
    group: FileGroup
    file_type: PathRole

    def __str__(self) -> str:
        return f'<{self.file_type.shortname}>/{self.group.group_path}'

@dataclass(frozen=True)
class Library:
    name: str

@dataclass(frozen=True)
class ExtensionConfig:
    header_extension: str
    src_extension: str

    def __post_init__(self) -> None:
        assert self.header_extension.startswith('.')
        assert self.src_extension.startswith('.')

@dataclass(frozen=True)
class LibraryRelPath:
    raw: PurePath

    @staticmethod
    def from_str(s: str) -> 'LibraryRelPath':
        return LibraryRelPath(PurePath(s))

    def __truediv__(self, other: Union[str, PurePath]) -> 'LibraryRelPath':
        return LibraryRelPath(self.raw / other)

    def to_repo_rel(self, library: Library) -> 'RepoRelPath':
        return RepoRelPath(PurePath('lib') / library.name / self.raw)

def get_absolute_path_for_file(
    repo: Repo,
    library: Library,
    file: File,
    extension_config: ExtensionConfig
) -> AbsolutePath:
    repo_rel = get_repo_rel_path_for_file_and_library(library, file, extension_config)

    return AbsolutePath(repo.raw / repo_rel.raw)

def get_repo_rel_path_for_file_and_library(
    library: Library,
    file: File,
    extension_config: ExtensionConfig,
) -> RepoRelPath:
    return get_path_for_file_and_library(library, file, extension_config).to_repo_rel(library)

def get_path_for_file_and_library(
    library: Library,
    file: File,
    extension_config: ExtensionConfig,
) -> LibraryRelPath:
        group_dir = file.group.group_path.parent
        group_name = file.group.group_path.name

        header_extension = extension_config.header_extension
        source_extension = extension_config.src_extension

        if file.file_type == PathRole.PUBLIC_HEADER:
            return LibraryRelPath.from_str('include') / library.name / group_dir / (group_name + header_extension)
        elif file.file_type == PathRole.SOURCE:
            return LibraryRelPath.from_str('src') / library.name / group_dir / (group_name + source_extension)
        elif file.file_type == PathRole.TEST:
            return LibraryRelPath.from_str('test/src') / library.name / group_dir / (group_name + source_extension)
        elif file.file_type == PathRole.BENCHMARK:
            return LibraryRelPath.from_str('benchmark/src') / library.name / group_dir / (group_name + source_extension)
        elif file.file_type == PathRole.STRUCT_TOML:
            return LibraryRelPath.from_str('include') / library.name / group_dir / (group_name + '.struct.toml')
        elif file.file_type == PathRole.ENUM_TOML:
            return LibraryRelPath.from_str('include') / library.name / group_dir / (group_name + '.enum.toml')
        elif file.file_type == PathRole.VARIANT_TOML:
            return LibraryRelPath.from_str('include') / library.name / group_dir / (group_name + '.variant.toml')
        elif file.file_type == PathRole.GENERATED_HEADER:
            return LibraryRelPath.from_str('include') / library.name / group_dir / (group_name + '.dtg' + header_extension)
        elif file.file_type == PathRole.GENERATED_SOURCE:
            return LibraryRelPath.from_str('include') / library.name / group_dir / (group_name + '.dtg' + source_extension)
        else:
            raise ValueError()
