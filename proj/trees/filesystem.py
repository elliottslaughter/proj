from .file_tree import MutableFileTreeWithMtime
from .file_trees.filesystem_file_tree import FilesystemFileTree
from proj.paths.absolute_path import AbsolutePath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from proj.paths import Repo

def load_root_filesystem() -> MutableFileTreeWithMtime:
    return FilesystemFileTree(AbsolutePath('/'))

def load_filesystem_for_repo(repo: 'Repo') -> MutableFileTreeWithMtime:
    fs = load_root_filesystem()

    return fs.restrict_to_subdir(repo.path)
