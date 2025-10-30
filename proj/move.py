from dataclasses import dataclass
from .config_file import (
    ExtensionConfig,
    ProjectConfig,
)
from pathlib import (
    Path,
)
from typing import (
    Set,
    Iterator,
)
from .paths import (
    RoleInGroup,
    FileGroup,
    File,
    RepoRelPath,
)
from .trees import (
    MutablePathTree,
    PathTree,
)
import io
from .utils import (
    nearest_common_ancestor,
)
from .parse_project import (
    parse_file_path,
)
from .unparse_project import get_repo_rel_path

@dataclass(frozen=True)
class ConcreteMove:
    src: RepoRelPath
    dst: RepoRelPath

def get_moves_for_group(
    repo_path_tree: PathTree, 
    src_group: FileGroup, 
    dst_group: FileGroup, 
    extension_config: ExtensionConfig,
) -> Iterator[ConcreteMove]:
    for role in RoleInGroup:
        src_path = get_repo_rel_path(File(src_group, role), extension_config)
        dst_path = get_repo_rel_path(File(dst_group, role), extension_config)

        if not repo_path_tree.has_path(src_path.path):
            continue
        assert repo_path_tree.has_file(src_path.path)
        assert not repo_path_tree.has_path(dst_path.path)

        yield ConcreteMove(src_path, dst_path)

def get_move_plan(
    repo_path_tree: PathTree,
    src_file: File, 
    dst_file: File, 
    extension_config: ExtensionConfig,
) -> Set[ConcreteMove]:
    assert src_file.role == dst_file.role

    return set(get_moves_for_group(repo_path_tree, src_file.group, dst_file.group, extension_config))

def pretty_print_move_plan(move_plan: Set[ConcreteMove]) -> str:
    s = io.StringIO()
    for move in move_plan:
        ancestor = nearest_common_ancestor(move.src.path, move.dst.path)
        src_rel = move.src.path.relative_to(ancestor)
        dst_rel = move.dst.path.relative_to(ancestor)
        s.write(f'{ancestor}/{{{src_rel} -> {dst_rel}}}\n')
    return s.getvalue()

def perform_file_group_move(
    extension_config: ExtensionConfig, 
    repo_path_tree: MutablePathTree, 
    src: RepoRelPath, 
    dst: RepoRelPath, 
    dry_run: bool,
) -> None:
    src_file = parse_file_path(src, extension_config)
    assert src_file is not None
    dst_file = parse_file_path(dst, extension_config)
    assert dst_file is not None

    move_plan = get_move_plan(repo_path_tree, src_file, dst_file, extension_config)
    if dry_run:
        output = pretty_print_move_plan(move_plan)
        print(output)
    for move in move_plan:
        repo_path_tree.mkdir(move.dst.path.parent, exist_ok=True, parents=True)
        repo_path_tree.rename(
            src=move.src.path,
            dst=move.dst.path,
        )
