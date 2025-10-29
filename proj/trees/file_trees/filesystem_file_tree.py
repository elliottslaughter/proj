from ..file_tree import FileTree
from ..path_trees.filesystem_path_tree import FilesystemPathTree
from pathlib import PurePath, Path
from ...paths.absolute_path import AbsolutePath

class FilesystemFileTree(FileTree, FilesystemPathTree):
    def get_file_contents(
        self,
        p: PurePath,
    ) -> str:
        assert self.has_file(p)
        return Path(p).read_text()

    def set_file_contents(
        self, 
        p: PurePath, 
        contents: str, 
        exist_ok: bool = False, 
        parents: bool = False,
    ) -> None:
        self.mkdir(p.parent, exist_ok=exist_ok, parents=parents)
        assert not self.has_file(p)
        Path(self._root.raw / p).write_text(contents)

    @staticmethod
    def for_path(path: PurePath) -> 'FilesystemFileTree':
        assert path.is_absolute()

        return FilesystemFileTree(AbsolutePath(path))
