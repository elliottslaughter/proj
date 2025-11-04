from dataclasses import dataclass
from .paths import (
    FileGroup,
    File,
    RoleInGroup,
    Component,
    ComponentRelPath,
    RepoRelPath,
)
from proj.trees import (
    PathTree,
    MaskedPathTree,
)
from typing import (
    Dict,
    Tuple,
    Set,
    FrozenSet,
    Iterator,
    Mapping,
    Collection,
    Iterable,
    List,
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
import logging

_l = logging.getLogger(__name__)

@dataclass(frozen=True)
class IncompleteGroup:
    file_group: FileGroup
    missing: FrozenSet[RoleInGroup]

@dataclass(frozen=True)
class UnrecognizedFile:
    path: ComponentRelPath

@dataclass(frozen=True)
class KnownFile:
    path: ComponentRelPath


def _scan_component_for_files(
    component: Component,
    component_path_tree: PathTree,
    extension_config: ExtensionConfig,
) -> Iterator[KnownFile | File | UnrecognizedFile]:
    _l.info('Scanning component %s', component)

    def try_to_recognize(
        p: PurePath
    ) -> KnownFile | File | UnrecognizedFile:
        component_rel_path = ComponentRelPath(p, component)

        if p.name == 'README.md':
            return KnownFile(component_rel_path)
        allowed_cmake_files = [
            PurePath('CMakeLists.txt'),
            PurePath('test/CMakeLists.txt'),
            PurePath('benchmark/CMakeLists.txt'),
        ]
        if p in allowed_cmake_files:
            return KnownFile(component_rel_path)

        file = parse_file_path(ComponentRelPath(p, component), extension_config)
        if file is not None:
            return file
        else:
            return UnrecognizedFile(component_rel_path)
    
    for file in map(try_to_recognize, component_path_tree.files()):
        _l.debug('Scanning component %s found file %s', component, file)
        yield file

def scan_component_for_files(
    component: Component,
    component_path_tree: PathTree,
    extension_config: ExtensionConfig,
) -> Set[KnownFile | File | UnrecognizedFile]:
    return set(_scan_component_for_files(component, component_path_tree, extension_config))

def _scan_repo_for_components(
    path_tree: PathTree,
    extension_config: ExtensionConfig,
) -> Iterator[Tuple[Component, PathTree]]:
    _l.debug('Scanning path_tree %s for files', path_tree)
    for p in path_tree.ls_dir(PurePath('lib')):
        if path_tree.has_dir(p):
            component = Component.library(p.name)
            subtree = path_tree.restrict_to_subdir(p)
            _l.debug('Scanning repo found component %s with tree %s', component, subtree)
            yield (component, subtree)

    bin_path = PurePath('bin')
    if path_tree.has_dir(bin_path):
        for p in path_tree.ls_dir(bin_path):
            if path_tree.has_dir(p):
                component = Component.executable(p.name)
                subtree = path_tree.restrict_to_subdir(p)
                _l.debug('Scanning repo found component %s with tree %s', component, subtree)
                yield (component, subtree)

def scan_repo_for_components(
    path_tree: PathTree,
    extension_config: ExtensionConfig,
) -> List[Tuple[Component, PathTree]]:
    return list(_scan_repo_for_components(path_tree, extension_config))

def scan_repo_for_files(
    repo_path_tree: PathTree,
    extension_config: ExtensionConfig,
) -> Iterator[KnownFile | File | UnrecognizedFile]:
    for component, component_tree in scan_repo_for_components(repo_path_tree, extension_config):
        for file in scan_component_for_files(component, component_tree, extension_config):
            yield file

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
    ignore_paths: Iterable[RepoRelPath],
) -> Iterator[IncompleteGroup | UnrecognizedFile]:
    _ignore_paths = list(ignore_paths)
    _l.debug("Layout check ignoring paths: %s", ignore_paths)

    masked_path_tree: PathTree = MaskedPathTree(
        repo_path_tree,
        [p.path for p in ignore_paths],
    )

    file_groups: Dict[FileGroup, Set[RoleInGroup]] = defaultdict(set)
    for file_found in scan_repo_for_files(masked_path_tree, extension_config):
        if isinstance(file_found, UnrecognizedFile):
            yield file_found
        elif isinstance(file_found, File):
            file_groups[file_found.group].add(file_found.role)
    yield from detect_incomplete_groups(file_groups)
