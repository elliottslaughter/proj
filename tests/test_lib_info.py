from proj.lib_info import (
    get_sublib_root,
    get_lib_info,
    LibInfo,
)
from proj.path_tree import (
    PathTree,
    PathType,
)
from pathlib import PurePath

def test_get_sublib_root() -> None:
    header_path = PurePath('lib/example/include/example/thing.h')

    repo_path_tree = PathTree.from_map({
        header_path: PathType.FILE,
        PurePath('lib/example/src/example/thing.cc'): PathType.FILE,
        PurePath('lib/example/test/src/example/thing.cc'): PathType.FILE,
    })

    result = get_sublib_root(repo_path_tree, header_path)
    correct = PurePath('lib/example')

    assert result == correct

def test_get_lib_info() -> None:
    header_path = PurePath('lib/example/include/example/thing.h')

    repo_path_tree = PathTree.from_map({
        header_path: PathType.FILE,
        PurePath('lib/example/src/example/thing.cc'): PathType.FILE,
        PurePath('lib/example/test/src/example/thing.cc'): PathType.FILE,
    })

    result = get_lib_info(repo_path_tree, header_path)
    
    correct = LibInfo(
        include_dir=PurePath('lib/include'),
        src_dir=PurePath('lib/src'),
        test_dir=None,
        benchmark_dir=None,
    )

    assert result == correct
