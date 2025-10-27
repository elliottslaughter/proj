from dataclasses import dataclass
from proj.paths import (
    FileGroup,
    File,
    PathRole,
    Library,
    ExtensionConfig,
    LibraryRelPath,
)
from proj.path_tree import PathTree
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
from proj.path_info import (
    get_file_for_path,
)
from collections import (
    defaultdict,
)

@dataclass(frozen=True)
class IncompleteGroup:
    library: Library
    file_group: FileGroup
    missing: FrozenSet[PathRole]

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
        if p == PurePath('CMakeLists.txt'):
            return KnownFile(p)

        file = get_file_for_path(library, LibraryRelPath(p), extension_config)
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

def detect_missing_roles(present: Collection[PathRole]) -> Set[PathRole]:
    required = {
        PathRole.PUBLIC_HEADER: {PathRole.SOURCE},
        PathRole.SOURCE: {PathRole.PUBLIC_HEADER},
        PathRole.TEST: {PathRole.SOURCE, PathRole.PUBLIC_HEADER},
        PathRole.BENCHMARK: {PathRole.SOURCE, PathRole.PUBLIC_HEADER},
    }

    necessary: Set[PathRole] = set()
    for role in present:
        if role in required:
            necessary.update(required[role])

    return necessary - set(present)


def detect_incomplete_groups(m: Mapping[Tuple[Library, FileGroup], Collection[PathRole]]) -> Iterator[IncompleteGroup]:
    for (library, file_group), path_roles in m.items():
        missing_roles = frozenset(detect_missing_roles(path_roles))
        if len(missing_roles) > 0:
            yield IncompleteGroup(
                library=library,
                file_group=file_group,
                missing=missing_roles,
            )

def run_layout_check(
    repo_path_tree: PathTree,
    extension_config: ExtensionConfig,
) -> Iterator[IncompleteGroup | UnrecognizedFile]:
    file_groups: Dict[Tuple[Library, FileGroup], Set[PathRole]] = defaultdict(set)
    for library, library_tree in scan_repo_for_libraries(repo_path_tree, extension_config):
        for file_found in scan_library_for_files(library, library_tree, extension_config):
            if isinstance(file_found, UnrecognizedFile):
                yield file_found
            elif isinstance(file_found, File):
                file_groups[(library, file_found.group)].add(file_found.file_type)
    yield from detect_incomplete_groups(file_groups)
