import hashlib
from typing import Optional
from proj.trees.file_tree import FileTree
from pathlib import PurePath


def get_file_hash(tree: FileTree, path: PurePath) -> Optional[bytes]:
    try:
        digest = hashlib.md5(tree.get_file_contents(path).encode('utf8'))
        return digest.digest()
    except FileNotFoundError:
        return None
