from proj.layout import (
    scan_library_for_files,
    KnownFile,
    UnrecognizedFile,
    run_layout_check,
    IncompleteGroup,
    scan_repo_for_libraries,
    detect_missing_roles,
)
from proj.paths import (
    Library,
    FileGroup,
    ExtensionConfig,
    PathRole,
)
from proj.path_tree import (
    EmulatedPathTree,
    PathType,
)
from pathlib import (
    PurePath,
)

def test_scan_library_for_files() -> None:
    library = Library('example')

    struct_toml = 'include/example/example_struct.struct.toml'
    header = 'include/example/example_struct.h'
    src_f = 'src/example/example_struct.cc'
    test_src = 'test/src/example/example_struct.cc'
    benchmark_src = 'benchmark/src/example/example_struct.cc'

    extension_config = ExtensionConfig(
        '.h', '.cc',
    )

    library_path_tree = EmulatedPathTree.from_map({
        p: PathType.FILE 
        for p in [
            'CMakeLists.txt',
            'include/example/example_variant.variant.toml',
            struct_toml,
            header,
            src_f,
            test_src,
            benchmark_src,
            'src/bad.cc'
        ]
    })

    result = set(scan_library_for_files(library, library_path_tree, extension_config))

    group = FileGroup(PurePath('example_struct'))

    correct = {
        KnownFile(PurePath('CMakeLists.txt')),
        group.struct_toml,
        group.public_header,
        group.source,
        group.test,
        group.benchmark,
        FileGroup(PurePath('example_variant')).variant_toml,
        UnrecognizedFile(PurePath('src/bad.cc'))
    }

    assert result == correct

def test_scan_repo_for_libraries() -> None:
    extension_config = ExtensionConfig(
        '.h', '.cc',
    )

    repo_path_tree = EmulatedPathTree.from_map({
        p: PathType.FILE
        for p in [
            'lib/example/CMakeLists.txt',
            'lib/example/include/example/example_variant.variant.toml',
            'lib/example/include/example/example_struct.struct.toml',
            'lib/example/src/example/example_struct.cc',
            'lib/example/test/src/example/example_struct.cc',
            'lib/example/benchmark/src/example/example_struct.cc',
            'lib/example/src/bad.cc',
        ]
    })

    lib_path_tree = EmulatedPathTree.from_map({
        p: PathType.FILE
        for p in [
            'CMakeLists.txt',
            'include/example/example_variant.variant.toml',
            'include/example/example_struct.struct.toml',
            'src/example/example_struct.cc',
            'test/src/example/example_struct.cc',
            'benchmark/src/example/example_struct.cc',
            'src/bad.cc',
        ]
    })
    
    result = {
        k: v for k, v in scan_repo_for_libraries(repo_path_tree, extension_config)
    }

    correct = {
        Library('example'): lib_path_tree,
    }

    assert set(result.keys()) == set(correct.keys())
    assert result[Library('example')] == lib_path_tree

def test_detect_missing_roles() -> None:
    result = detect_missing_roles({
        PathRole.SOURCE,
        PathRole.STRUCT_TOML,
        PathRole.TEST,
        PathRole.BENCHMARK,
    })

    correct = {PathRole.PUBLIC_HEADER}

    assert correct == result

def test_run_layout_check() -> None:
    library = Library('example')

    struct_toml = 'lib/example/include/example/example_struct.struct.toml'
    src_f = 'lib/example/src/example/example_struct.cc'
    test_src = 'lib/example/test/src/example/example_struct.cc'
    benchmark_src = 'lib/example/benchmark/src/example/example_struct.cc'

    extension_config = ExtensionConfig(
        '.h', '.cc',
    )

    library_path_tree = EmulatedPathTree.from_map({
        p: PathType.FILE 
        for p in [
            'lib/example/CMakeLists.txt',
            'lib/example/include/example/example_variant.variant.toml',
            struct_toml,
            src_f,
            test_src,
            benchmark_src,
            'lib/example/src/bad.cc'
        ]
    })

    result = set(run_layout_check(library_path_tree, extension_config))

    group = FileGroup(PurePath('example_struct'))

    correct = {
        IncompleteGroup(library, group, frozenset({PathRole.PUBLIC_HEADER})),
        UnrecognizedFile(PurePath('src/bad.cc'))
    }

    assert result == correct
