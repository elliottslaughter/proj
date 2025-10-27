from typing import (
    Iterator,
    Set,
)
import itertools
from proj.paths import (
    ExtensionConfig,
    RepoRelPath,
    File,
    FileGroup,
    PathRole,
)
from proj.path_tree import (
    RepoPathTree,
)
from proj.path_info import (
    get_library_and_file_for_path,
)
from proj.paths import (
    get_path_for_file_and_library,
)

def get_possible_spec_files(file_group: FileGroup) -> Set[File]:
    return {
        File(file_group, PathRole.STRUCT_TOML),
        File(file_group, PathRole.ENUM_TOML),
        File(file_group, PathRole.VARIANT_TOML),
    }

def find_outdated(repo_path_tree: RepoPathTree, extension_config: ExtensionConfig) -> Iterator[RepoRelPath]:
    for p in itertools.chain(
        repo_path_tree.with_extension(".dtg" + extension_config.header_extension),
        repo_path_tree.with_extension(".dtg" + extension_config.src_extension),
    ):
        library, file = get_library_and_file_for_path(p, extension_config)

        possible_spec_paths = {
            get_path_for_file_and_library(library, file, extension_config)
            for spec_file in get_possible_spec_files(file.group)
        }
        
        if not any(
            repo_path_tree.has_file(possible_spec_path.to_repo_rel(library))
            for possible_spec_path in possible_spec_paths
        ):
            yield p
