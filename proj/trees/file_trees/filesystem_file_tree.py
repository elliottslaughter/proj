from ..file_tree import MutableFileTreeWithMtime
from ..path_trees.filesystem_path_tree import FilesystemPathTree
from pathlib import PurePath, Path
from ...paths.absolute_path import AbsolutePath

class FilesystemFileTree(MutableFileTreeWithMtime, FilesystemPathTree):
    def get_file_contents(
        self,
        p: PurePath,
    ) -> str:
        assert self.has_file(p), p
        return (self._root.raw / p).read_text()

    def set_file_contents(
        self, 
        p: PurePath, 
        contents: str, 
        exist_ok: bool = False, 
        parents: bool = False,
    ) -> None:
        self.mkdir(p.parent, exist_ok=True, parents=parents)
        if not exist_ok:
            assert not self.has_file(p), p
        Path(self._root.raw / p).write_text(contents)

    def get_mtime(self, p: PurePath) -> float:
        assert self.has_file(p), p
        return Path(self._root.raw / p).stat().st_mtime

    @staticmethod
    def for_path(path: PurePath) -> 'FilesystemFileTree':
        assert path.is_absolute()

        return FilesystemFileTree(AbsolutePath(path))
