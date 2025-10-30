from dataclasses import dataclass
from .paths import (
    FileGroup,
    File,
    RoleInGroup,
    Library,
    LibraryRelPath,
)
from proj.trees import PathTree
from typing import (
    Dict,
    Tuple,
    Set,
    FrozenSet,
    Iterator,
    Mapping,
    Collection,
)
from pathlib import (
    PurePath
)
from .parse_project import (
    parse_file_path,
)
from collections import (
    defaultdict,
)
from .config_file import ExtensionConfig

@dataclass(frozen=True)
class IncompleteGroup:
    file_group: FileGroup
    missing: FrozenSet[RoleInGroup]

@dataclass(frozen=True)
class UnrecognizedFile:
    path: PurePath

@dataclass(frozen=True)
class KnownFile:
    path: PurePath


def scan_library_for_files(
    library: Library,
    library_path_tree: PathTree,
    extension_config: ExtensionConfig,
) -> Iterator[KnownFile | File | UnrecognizedFile]:
    def try_to_recognize(
        p: PurePath
    ) -> KnownFile | File | UnrecognizedFile:
        if p.name == 'README.md':
            return KnownFile(p)
        allowed_cmake_files = [
            PurePath('CMakeLists.txt'),
            PurePath('test/CMakeLists.txt'),
            PurePath('benchmark/CMakeLists.txt'),
        ]
        if p in allowed_cmake_files:
            return KnownFile(p)

        file = parse_file_path(LibraryRelPath(p, library), extension_config)
        if file is not None:
            return file
        else:
            return UnrecognizedFile(p)
    
    yield from map(try_to_recognize, library_path_tree.files())

def scan_repo_for_libraries(
    path_tree: PathTree,
    extension_config: ExtensionConfig,
) -> Iterator[Tuple[Library, PathTree]]:
    for p in path_tree.ls_dir(PurePath('lib')):
        if path_tree.has_dir(p):
            yield (Library(p.name), path_tree.restrict_to_subdir(p))

def detect_missing_roles(present: Collection[RoleInGroup]) -> Set[RoleInGroup]:
    required = {
        RoleInGroup.PUBLIC_HEADER: {RoleInGroup.SOURCE},
        RoleInGroup.SOURCE: {RoleInGroup.PUBLIC_HEADER},
        RoleInGroup.TEST: {RoleInGroup.SOURCE, RoleInGroup.PUBLIC_HEADER},
        RoleInGroup.BENCHMARK: {RoleInGroup.SOURCE, RoleInGroup.PUBLIC_HEADER},
    }

    necessary: Set[RoleInGroup] = set()
    for role in present:
        if role in required:
            necessary.update(required[role])

    return necessary - set(present)


def detect_incomplete_groups(m: Mapping[FileGroup, Collection[RoleInGroup]]) -> Iterator[IncompleteGroup]:
    allowlist = [
        PurePath('main'),
    ]
    for file_group, path_roles in m.items():
        missing_roles = frozenset(detect_missing_roles(path_roles))
        if len(missing_roles) > 0 and file_group.group_path not in allowlist:
            yield IncompleteGroup(
                file_group=file_group,
                missing=missing_roles,
            )

def run_layout_check(
    repo_path_tree: PathTree,
    extension_config: ExtensionConfig,
) -> Iterator[IncompleteGroup | UnrecognizedFile]:
    file_groups: Dict[FileGroup, Set[RoleInGroup]] = defaultdict(set)
    for library, library_tree in scan_repo_for_libraries(repo_path_tree, extension_config):
        for file_found in scan_library_for_files(library, library_tree, extension_config):
            if isinstance(file_found, UnrecognizedFile):
                yield file_found
            elif isinstance(file_found, File):
                file_groups[file_found.group].add(file_found.role)
    yield from detect_incomplete_groups(file_groups)
