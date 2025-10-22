from proj.path_tree import (
    RelativePathTree,
    AbsolutePathTree,
)
from pathlib import (
    Path,
    PurePath,
)
from .project_utils import (
    TemporaryDirectory,
)

def test_relative_path_tree() -> None:
    with TemporaryDirectory() as _d:
        d = Path(_d)
        (d / 'hello.txt').touch()
        (d / 'a' / 'b.c').mkdir(parents=True, exist_ok=False)
        (d / 'a' / 'goodbye.py').touch()
        
        tree = RelativePathTree.from_fs(d)

    correct = RelativePathTree({
        PurePath('.'): False,
        PurePath('hello.txt'): True,
        PurePath('a/'): False,
        PurePath('a/b.c'): False,
        PurePath('a/goodbye.py'): True,
    })

    assert tree == correct

def test_absolute_path_tree() -> None:
    with TemporaryDirectory() as _d:
        d = Path(_d)
        (d / 'hello.txt').touch()
        (d / 'a' / 'b.c').mkdir(parents=True, exist_ok=False)
        (d / 'a' / 'goodbye.py').touch()
        
        tree = AbsolutePathTree.from_fs(d)

    correct = AbsolutePathTree(
        d,
        RelativePathTree({
            PurePath('.'): False,
            PurePath('hello.txt'): True,
            PurePath('a/'): False,
            PurePath('a/b.c'): False,
            PurePath('a/goodbye.py'): True,
        })
    )

    assert tree == correct
