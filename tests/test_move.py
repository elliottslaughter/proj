from proj.move import (
    get_move_plan,
    ConcreteMove,
    perform_file_group_move,
)
from proj.trees import (
    PathType,
    EmulatedPathTree,
)
from proj.paths import (
    RepoRelPath,
    Library,
    FileGroup,
    File,
    RoleInGroup,
)
from proj.config_file import (
    ExtensionConfig,
)
from pathlib import PurePath
import copy

EXTENSION_CONFIG = ExtensionConfig(
    '.h',
    '.cc',
)

def test_get_move_plan() -> None:
    struct_toml = 'lib/person/include/person/example_struct.dtg.toml'
    header = 'lib/person/include/person/example_struct.h'
    src_f = 'lib/person/src/person/example_struct.cc'
    test_src = 'lib/person/test/src/person/example_struct.cc'
    benchmark_src = 'lib/person/benchmark/src/person/example_struct.cc'

    repo_path_tree = EmulatedPathTree.from_map({
        PurePath(p): PathType.FILE 
        for p in [
            'CMakeLists.txt',
            '.proj.toml',
            'lib/CMakeLists.txt',
            'lib/person/CMakeLists.txt',
            'lib/person/include/person/example_variant.dtg.toml',
            'lib/person/src/person/out_of_date2.dtg.cc',
            'lib/airplane/include/airplane/my_airplane.dtg.toml',
            struct_toml,
            header,
            src_f,
            test_src,
            benchmark_src,
        ]
    })

    src_library = Library('person')

    src = File(
        FileGroup(PurePath('example_struct'), src_library),
        RoleInGroup.SOURCE,
    )

    dst_library = Library('airplane')

    dst = File(
        FileGroup(PurePath('my_other_airplane'), dst_library),
        RoleInGroup.SOURCE,
    )

    def move(s: str, d: str) -> ConcreteMove:
        return ConcreteMove(
            RepoRelPath(PurePath(s)),
            RepoRelPath(PurePath(d)),
        )

    result = get_move_plan(repo_path_tree, src, dst, EXTENSION_CONFIG)
    correct = {
        move(struct_toml, 'lib/airplane/include/airplane/my_other_airplane.dtg.toml'),
        move(header, 'lib/airplane/include/airplane/my_other_airplane.h'),
        move(src_f, 'lib/airplane/src/airplane/my_other_airplane.cc'),
        move(test_src, 'lib/airplane/test/src/airplane/my_other_airplane.cc'),
        move(benchmark_src, 'lib/airplane/benchmark/src/airplane/my_other_airplane.cc'),
    }

    assert result == correct

def test_perform_file_group_move() -> None:
    repo_path_tree = EmulatedPathTree.from_map({
        PurePath(p): PathType.FILE 
        for p in [
            'CMakeLists.txt',
            '.proj.toml',
            'lib/CMakeLists.txt',
            'lib/person/CMakeLists.txt',
            'lib/person/include/person/example_variant.dtg.toml',
            'lib/person/src/person/out_of_date2.dtg.cc',
            'lib/airplane/include/airplane/my_airplane.dtg.toml',
            'lib/person/include/person/example_struct.dtg.toml',
            'lib/person/include/person/example_struct.h',
            'lib/person/src/person/example_struct.cc',
            'lib/person/test/src/person/example_struct.cc',
            'lib/person/benchmark/src/person/example_struct.cc',
        ]
    })

    src = RepoRelPath(PurePath('lib/person/src/person/example_struct.cc'))
    dst = RepoRelPath(PurePath('lib/airplane/src/airplane/example_airplane.cc'))

    perform_file_group_move(
        EXTENSION_CONFIG,
        repo_path_tree,
        src,
        dst,
        dry_run=False,
    )

    correct = EmulatedPathTree.from_lists(
        files=[
            'CMakeLists.txt',
            '.proj.toml',
            'lib/CMakeLists.txt',
            'lib/person/CMakeLists.txt',
            'lib/person/include/person/example_variant.dtg.toml',
            'lib/person/src/person/out_of_date2.dtg.cc',
            'lib/airplane/include/airplane/my_airplane.dtg.toml',
            'lib/airplane/include/airplane/example_airplane.dtg.toml',
            'lib/airplane/include/airplane/example_airplane.h',
            'lib/airplane/src/airplane/example_airplane.cc',
            'lib/airplane/test/src/airplane/example_airplane.cc',
            'lib/airplane/benchmark/src/airplane/example_airplane.cc',
        ],
        dirs=[
            'lib/person/include/person/',
            'lib/person/src/person/',
            'lib/person/test/src/person/',
            'lib/person/benchmark/src/person/',
        ]
    )

    assert repo_path_tree == correct

def test_perform_file_group_move_to_directory() -> None:
    repo_path_tree = EmulatedPathTree.from_map({
        PurePath(p): PathType.FILE 
        for p in [
            'CMakeLists.txt',
            '.proj.toml',
            'lib/CMakeLists.txt',
            'lib/person/CMakeLists.txt',
            'lib/person/include/person/example_variant.dtg.toml',
            'lib/person/src/person/out_of_date2.dtg.cc',
            'lib/airplane/include/airplane/my_airplane.dtg.toml',
            'lib/person/include/person/example_struct.dtg.toml',
            'lib/person/include/person/example_struct.h',
            'lib/person/src/person/example_struct.cc',
            'lib/person/test/src/person/example_struct.cc',
            'lib/person/benchmark/src/person/example_struct.cc',
        ]
    })

    src = RepoRelPath(PurePath('lib/person/src/person/example_struct.cc'))
    dst = RepoRelPath(PurePath('lib/airplane/src/airplane/'))

    perform_file_group_move(
        EXTENSION_CONFIG,
        repo_path_tree,
        src,
        dst,
        dry_run=False,
    )
    correct = EmulatedPathTree.from_lists(
        files=[
            'CMakeLists.txt',
            '.proj.toml',
            'lib/CMakeLists.txt',
            'lib/person/CMakeLists.txt',
            'lib/person/include/person/example_variant.dtg.toml',
            'lib/person/src/person/out_of_date2.dtg.cc',
            'lib/airplane/include/airplane/my_airplane.dtg.toml',
            'lib/airplane/include/airplane/example_struct.dtg.toml',
            'lib/airplane/include/airplane/example_struct.h',
            'lib/airplane/src/airplane/example_struct.cc',
            'lib/airplane/test/src/airplane/example_struct.cc',
            'lib/airplane/benchmark/src/airplane/example_struct.cc',
        ],
        dirs=[
            'lib/person/include/person/',
            'lib/person/src/person/',
            'lib/person/test/src/person/',
            'lib/person/benchmark/src/person/',
        ]
    )

    assert repo_path_tree == correct

def test_perform_file_group_move_to_current_location() -> None:
    repo_path_tree = EmulatedPathTree.from_map({
        PurePath(p): PathType.FILE 
        for p in [
            'CMakeLists.txt',
            '.proj.toml',
            'lib/CMakeLists.txt',
            'lib/person/CMakeLists.txt',
            'lib/person/include/person/example_variant.dtg.toml',
            'lib/person/src/person/out_of_date2.dtg.cc',
            'lib/airplane/include/airplane/my_airplane.dtg.toml',
            'lib/person/include/person/example_struct.dtg.toml',
            'lib/person/include/person/example_struct.h',
            'lib/person/src/person/example_struct.cc',
            'lib/person/test/src/person/example_struct.cc',
            'lib/person/benchmark/src/person/example_struct.cc',
        ]
    })

    correct = copy.deepcopy(repo_path_tree)

    src = RepoRelPath(PurePath('lib/person/src/person/example_struct.cc'))
    dst = src

    perform_file_group_move(
        EXTENSION_CONFIG,
        repo_path_tree,
        src,
        dst,
        dry_run=False,
    )

    assert repo_path_tree == correct
