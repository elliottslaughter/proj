from dataclasses import dataclass
from .config_file import (
    load_repo_path_tree,
    load_config,
    find_config_root,
)
from pathlib import (
    Path,
)
from typing import (
    Set,
    Iterator,
)
from .path_info import (
    PathRole,
    get_library_and_file_for_path,
)
from .paths import (
    Library,
    FileGroup,
    get_repo_rel_path_for_file_and_library,
    File,
    ExtensionConfig,
    RepoRelPath,
    get_repo_rel_path,
)
from .path_tree import (
    RepoPathTree,
)

@dataclass(frozen=True)
class ConcreteMove:
    src: RepoRelPath
    dst: RepoRelPath

def get_moves_for_group(repo_path_tree: RepoPathTree, src_library: Library, src_group: FileGroup, dst_library: Library, dst_group: FileGroup, extension_config: ExtensionConfig) -> Iterator[ConcreteMove]:
    for role in PathRole:
        src_path = get_repo_rel_path_for_file_and_library(src_library, File(src_group, role), extension_config)
        dst_path = get_repo_rel_path_for_file_and_library(dst_library, File(dst_group, role), extension_config)

        if not repo_path_tree.has_path(src_path):
            continue
        assert repo_path_tree.has_file(src_path)
        assert not repo_path_tree.has_path(dst_path)

        yield ConcreteMove(src_path, dst_path)

def get_move_plan(repo_path_tree: RepoPathTree, src: RepoRelPath, dst: RepoRelPath, extension_config: ExtensionConfig) -> Set[ConcreteMove]:
    (src_library, src_file) = get_library_and_file_for_path(src, extension_config)
    (dst_library, dst_file) = get_library_and_file_for_path(dst, extension_config)

    assert src_file.file_type == dst_file.file_type

    return set(get_moves_for_group(repo_path_tree, src_library, src_file.group, dst_library, dst_file.group, extension_config))

def execute_move(src: Path, dst: Path) -> None:
    assert src.is_absolute()
    assert dst.is_absolute()

    repo = find_config_root(src)
    assert repo is not None
    assert dst.is_relative_to(repo.raw)

    repo_path_tree = load_repo_path_tree(src)
    assert repo_path_tree is not None
    config = load_config(repo)

    src_rel = get_repo_rel_path(repo, src)
    dst_rel = get_repo_rel_path(repo, dst)

    move_plan = get_move_plan(repo_path_tree, src_rel, dst_rel, config.extension_config)
    print(f'{move_plan=}')
