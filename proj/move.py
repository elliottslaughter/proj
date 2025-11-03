from dataclasses import dataclass
from .config_file import (
    ExtensionConfig,
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
    FileTree,
    PathTree,
    TracedMutableFileTree,
    TracedMutablePathTree,
    MutablePathTree,
    MutableFileTree,
    MutableTracedFileTreeByWrapping,
    MutableTracedPathTreeByWrapping,
    EmulatedFileTree,
    EmulatedPathTree,
)
import io
from .utils import (
    nearest_common_ancestor,
)
from .parse_project import (
    parse_file_path,
)
from .unparse_project import get_repo_rel_path
from .layout import scan_repo_for_files
from .includes import (
    replace_file_group_include_in_cpp_file_contents,
    replace_file_group_include_in_dtg_toml_file_contents,
)
from .diff import (
    render_file_diff,
    render_path_diff,
)
from .ifndef import (
    fix_ifndefs_in_file,
)

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

    if src_file.group == dst_file.group:
        return set()

    return set(get_moves_for_group(repo_path_tree, src_file.group, dst_file.group, extension_config))

def pretty_print_move_plan(move_plan: Set[ConcreteMove]) -> str:
    s = io.StringIO()
    for move in move_plan:
        ancestor = nearest_common_ancestor(move.src.path, move.dst.path)
        src_rel = move.src.path.relative_to(ancestor)
        dst_rel = move.dst.path.relative_to(ancestor)
        s.write(f'{ancestor}/{{{src_rel} -> {dst_rel}}}\n')
    return s.getvalue()

def _perform_file_group_move(
    repo_path_tree: MutablePathTree, 
    src_file: File, 
    dst_file: File, 
    extension_config: ExtensionConfig, 
    dry_run: bool,
) -> None:

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

def file_tree_to_emulated(tree: FileTree) -> EmulatedFileTree:
    return EmulatedFileTree.from_lists(
        curr_time=0.0,
        files=[
            (f, 0.0, tree.get_file_contents(f))
            for f in tree.files()
        ],
        dirs=[
            (d, 0.0) for d in tree.dirs()    
        ],
    )

def path_tree_to_emulated(tree: PathTree) -> EmulatedPathTree:
    return EmulatedPathTree.from_lists(
        files=[f for f in tree.files()],
        dirs=[d for d in tree.dirs()],
    )


def perform_file_group_move(
    repo_path_tree: MutablePathTree, 
    src: RepoRelPath,
    dst: RepoRelPath,
    extension_config: ExtensionConfig, 
    dry_run: bool,
) -> None:
    if dry_run:
        repo_path_tree = MutableTracedPathTreeByWrapping(
            path_tree_to_emulated(repo_path_tree),
        )

    src_file = parse_file_path(src, extension_config)
    assert src_file is not None

    dst_file = parse_file_path(dst, extension_config)
    if dst_file is None:
        dst_file = parse_file_path(dst / src.name, extension_config)
    assert dst_file is not None

    _perform_file_group_move(
        repo_path_tree=repo_path_tree,
        src_file=src_file,
        dst_file=dst_file,
        extension_config=extension_config,
        dry_run=dry_run,
    )

    if dry_run:
        assert isinstance(repo_path_tree, TracedMutablePathTree)
        print(render_path_diff(repo_path_tree.get_path_trace()))


def perform_file_group_move_with_include_and_ifndef_update(
    repo_path_tree: MutableFileTree,
    src: RepoRelPath,
    dst: RepoRelPath,
    extension_config: ExtensionConfig,
    ifndef_base: str,
    update_includes: bool,
    update_ifndefs: bool,
    dry_run: bool,
) -> None:
    if dry_run:
        repo_path_tree = MutableTracedFileTreeByWrapping(
            file_tree_to_emulated(repo_path_tree),
        )

    src_file = parse_file_path(src, extension_config)
    assert src_file is not None

    dst_file = parse_file_path(dst, extension_config)
    if dst_file is None:
        dst_file = parse_file_path(dst / src.name, extension_config)
    assert dst_file is not None

    _perform_file_group_move(
        repo_path_tree=repo_path_tree,
        src_file=src_file,
        dst_file=dst_file,
        extension_config=extension_config,
        dry_run=dry_run,
    )

    if update_ifndefs:
        fix_ifndefs_in_file(
            repo_path_tree,
            dst_file.group.public_header,
            ifndef_base,
            extension_config,
            must_exist=False,
        )
        fix_ifndefs_in_file(
            repo_path_tree,
            dst_file.group.generated_header,
            ifndef_base,
            extension_config,
            must_exist=False,
        )

    if update_includes:
        for file in scan_repo_for_files(repo_path_tree, extension_config):
            if isinstance(file, File):
                file_path = get_repo_rel_path(file, extension_config).path
                if file.role == RoleInGroup.DTGEN_TOML:
                    file_contents = repo_path_tree.get_file_contents(file_path)
                    updated_contents = replace_file_group_include_in_cpp_file_contents(
                        contents=file_contents,
                        curr=src_file.group,
                        goal=dst_file.group,
                        header_extension=extension_config.header_extension,
                    )
                    repo_path_tree.set_file_contents(
                        file_path, 
                        updated_contents,
                        exist_ok=True,
                    )
                else:
                    file_contents = repo_path_tree.get_file_contents(file_path)
                    updated_contents = replace_file_group_include_in_dtg_toml_file_contents(
                        contents=file_contents,
                        curr=src_file.group,
                        goal=dst_file.group,
                        header_extension=extension_config.header_extension,
                    )
                    repo_path_tree.set_file_contents(
                        file_path, 
                        updated_contents,
                        exist_ok=True,
                    )

    if dry_run:
        assert isinstance(repo_path_tree, TracedMutableFileTree)
        print(render_file_diff(repo_path_tree.get_file_trace()))
