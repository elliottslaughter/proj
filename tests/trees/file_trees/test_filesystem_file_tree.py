from proj.trees import (
    FilesystemFileTree,
)
from proj.paths import AbsolutePath
from pathlib import PurePath, Path

DIR = Path(__file__).parent

def test_filesystem_file_tree():
    file_tree = FilesystemFileTree(
        AbsolutePath('/'),
    )

    sub_file_tree = file_tree.restrict_to_subdir(DIR)
    assert PurePath('test_filesystem_file_tree.py') in set(sub_file_tree.files())

def test_filesystem_file_tree_ls_dir():
    file_tree = FilesystemFileTree(
        AbsolutePath('/'),
    )

    sub_file_tree = file_tree.restrict_to_subdir(DIR)
    ls_result = set(sub_file_tree.ls_dir(PurePath('.')))
    assert PurePath('test_filesystem_file_tree.py') in ls_result
