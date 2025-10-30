from typing import (
    Iterator,
    List,
)
import itertools
from proj.paths import (
    RepoRelPath,
)
from proj.trees import (
    PathTree,
)
from proj.config_file import ExtensionConfig
from proj.parse_project import parse_file_path
from proj.unparse_project import get_repo_rel_path

def find_outdated(repo_path_tree: PathTree, extension_config: ExtensionConfig) -> List[RepoRelPath]:
    return list(_find_outdated(repo_path_tree, extension_config))

def _find_outdated(repo_path_tree: PathTree, extension_config: ExtensionConfig) -> Iterator[RepoRelPath]:
    for p in itertools.chain(
        repo_path_tree.with_extension(".dtg" + extension_config.header_extension),
        repo_path_tree.with_extension(".dtg" + extension_config.src_extension),
    ):
        file = parse_file_path(RepoRelPath(p), extension_config)
        assert file is not None

        spec_path = get_repo_rel_path(file.group.dtgen_toml, extension_config)
        
        if not repo_path_tree.has_file(spec_path.path):
            yield RepoRelPath(p)
