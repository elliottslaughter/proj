from dataclasses import dataclass
from pathlib import PurePath
from proj.trees.file_trees.filesystem_file_tree import FilesystemFileTree

@dataclass(frozen=True)
class Repo:
    path: PurePath
