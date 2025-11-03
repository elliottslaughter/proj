import re
from typing import (
    Optional,
)
from proj.paths import (
    RepoRelPath,
)
from .trees import MutableFileTree
from .paths import (
    File,
    RoleInGroup,
)
from .config_file import ExtensionConfig
from .unparse_project import get_repo_rel_path

def get_correct_ifndef_for_path(ifndef_base: str, repo_rel: RepoRelPath) -> str:
    unfixed = f"_{ifndef_base}_" + str(repo_rel.path)
    return re.sub(r"[^a-zA-Z0-9_]", "_", unfixed).upper()

def get_current_ifndef(contents: str) -> Optional[str]:
    m = re.search(r'#ifndef\s+(?P<ifndef>\w+)', contents)
    if m is None:
        return None

    return m.group('ifndef')

def set_ifndef(contents: str, ifndef: str) -> str:
    assert ' ' not in ifndef
    curr_ifndef = get_current_ifndef(contents)
    assert curr_ifndef is not None
    return contents.replace(curr_ifndef, ifndef)

def fix_ifndefs_in_file(
    repo_path_tree: MutableFileTree,
    file: File,
    ifndef_base: str,
    extension_config: ExtensionConfig,
    must_exist: bool,
) -> None:
    assert file.role in [RoleInGroup.PUBLIC_HEADER, RoleInGroup.GENERATED_HEADER]

    repo_rel_file_path = get_repo_rel_path(file, extension_config)

    if not repo_path_tree.has_file(repo_rel_file_path.path):
        if must_exist:
            raise RuntimeError()
        else:
            return

    correct_ifndef = get_correct_ifndef_for_path(ifndef_base, repo_rel_file_path)
    file_contents = repo_path_tree.get_file_contents(repo_rel_file_path.path)
    updated_contents = set_ifndef(
        contents=file_contents,
        ifndef=correct_ifndef,
    )
    repo_path_tree.set_file_contents(
        repo_rel_file_path.path, 
        updated_contents,
        exist_ok=True,
    )
