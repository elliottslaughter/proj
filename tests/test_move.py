from proj.move import (
    get_move_plan,
    ConcreteMove,
)
from proj.path_tree import (
    RepoPathTree,
    PathType,
    EmulatedPathTree,
)
from proj.paths import (
    RepoRelPath,
)
from proj.paths import (
    ExtensionConfig,
)
from pathlib import PurePath

EXTENSION_CONFIG = ExtensionConfig(
    '.h',
    '.cc',
)

def test_get_move_plan() -> None:
    struct_toml = 'lib/person/include/person/example_struct.struct.toml'
    header = 'lib/person/include/person/example_struct.h'
    src_f = 'lib/person/src/person/example_struct.cc'
    test_src = 'lib/person/test/src/person/example_struct.cc'
    benchmark_src = 'lib/person/benchmark/src/person/example_struct.cc'

    repo_path_tree: RepoPathTree = RepoPathTree(
        EmulatedPathTree.from_map({
            p: PathType.FILE 
            for p in [
                'CMakeLists.txt',
                '.proj.toml',
                'lib/CMakeLists.txt',
                'lib/person/CMakeLists.txt',
                'lib/person/include/person/example_variant.variant.toml',
                'lib/person/src/person/out_of_date2.dtg.cc',
                'lib/airplane/include/airplane/my_airplane.struct.toml',
                struct_toml,
                header,
                src_f,
                test_src,
                benchmark_src,
            ]
        })
    )

    src = RepoRelPath(PurePath(
        'lib/person/src/person/example_struct.cc'
    ))

    dst = RepoRelPath(PurePath(
        'lib/airplane/src/airplane/my_other_airplane.cc'
    ))

    def move(s: str, d: str) -> ConcreteMove:
        return ConcreteMove(
            RepoRelPath(PurePath(s)),
            RepoRelPath(PurePath(d)),
        )

    result = get_move_plan(repo_path_tree, src, dst, EXTENSION_CONFIG)
    correct = {
        move(struct_toml, 'lib/airplane/include/airplane/my_other_airplane.struct.toml'),
        move(header, 'lib/airplane/include/airplane/my_other_airplane.h'),
        move(src_f, 'lib/airplane/src/airplane/my_other_airplane.cc'),
        move(test_src, 'lib/airplane/test/src/airplane/my_other_airplane.cc'),
        move(benchmark_src, 'lib/airplane/benchmark/src/airplane/my_other_airplane.cc'),
    }

    assert result == correct
