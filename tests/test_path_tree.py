from proj.path_tree import (
    RepoPathTree,
    EmulatedPathTree,
    PathTree,
    PathType,
)
from proj.paths import (
    RepoRelPath,
)
from pathlib import (
    PurePath,
)
# from .project_utils import (
#     TemporaryDirectory,
# )

def test_emulated_path_tree_restrict_to_subdir():
    lib_path_tree = EmulatedPathTree.from_map({
        p: PathType.FILE
        for p in [
            'CMakeLists.txt',
            'include/example/example_variant.variant.toml',
            'include/example/example_struct.struct.toml',
            'src/example/example_struct.cc',
        ]
    })

    result = lib_path_tree.restrict_to_subdir(PurePath('include/example'))

    correct = EmulatedPathTree.from_map({
        p: PathType.FILE
        for p in [
            'example_variant.variant.toml',
            'example_struct.struct.toml',
        ]
    })

    assert result == correct

# def test_relative_path_tree() -> None:
#     with TemporaryDirectory() as _d:
#         d = Path(_d)
#         (d / 'hello.txt').touch()
#         (d / 'a' / 'b.c').mkdir(parents=True, exist_ok=False)
#         (d / 'a' / 'goodbye.py').touch()
#
#         tree = RelativePathTree.from_fs(d)
#
#     correct = RelativePathTree({
#         PurePath('.'): False,
#         PurePath('hello.txt'): True,
#         PurePath('a/'): False,
#         PurePath('a/b.c'): False,
#         PurePath('a/goodbye.py'): True,
#     })
#
#     assert tree == correct
