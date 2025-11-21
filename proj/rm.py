from .config_file import (
    ExtensionConfig,
)
from .paths import (
    RoleInGroup,
    FileGroup,
    File,
    RepoRelPath,
)
from .trees import (
    MutablePathTree,
    replay_trace_on_path_tree,
)
from .dry_run import load_repo_path_tree_for_dry_run
from .parse_project import (
    parse_file_path,
)
from .unparse_project import get_repo_rel_path
from .diff import render_path_diff

def _perform_file_group_rm(
    repo_path_tree: MutablePathTree,
    target_group: FileGroup,
    extension_config: ExtensionConfig,
) -> None:
    for role in RoleInGroup:
        target_path = get_repo_rel_path(File(target_group, role), extension_config)

        if repo_path_tree.has_path(target_path.path):
            assert repo_path_tree.has_file(target_path.path)
            repo_path_tree.rm_file(target_path.path)
            

def rm_file_group(
    repo_path_tree: MutablePathTree,
    target: RepoRelPath,
    extension_config: ExtensionConfig,
    dry_run: bool,
) -> None:
    mock_path_tree = load_repo_path_tree_for_dry_run(repo_path_tree)

    target_file = parse_file_path(target, extension_config)
    assert target_file is not None

    _perform_file_group_rm(
        repo_path_tree=mock_path_tree,
        target_group=target_file.group,
        extension_config=extension_config,
    )

    trace = mock_path_tree.get_path_trace()

    if dry_run:
        print(render_path_diff(trace))
    else:
        replay_trace_on_path_tree(trace, repo_path_tree)
