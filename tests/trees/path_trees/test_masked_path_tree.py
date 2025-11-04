from proj.trees import (
    EmulatedPathTree,
    PathType,
    MaskedPathTree,
)
from pathlib import PurePath

def test_masked_path_tree():
    example_variant_path = PurePath('include/example/example_variant.dtg.toml')
    cmakelists_path = PurePath('CMakeLists.txt')
    example_struct_toml_path = PurePath('include/example/something/example_struct.dtg.toml')
    example_struct2_toml_path = PurePath('include/example2/example2_struct.dtg.toml')
    example_struct_cc_path = PurePath('src/example/example_struct.cc')

    path_tree = EmulatedPathTree.from_map({
        p: PathType.FILE
        for p in [
            cmakelists_path,
            example_struct_toml_path,
            example_struct_cc_path,
            example_variant_path,
            example_struct2_toml_path,
        ]
    })

    masked_path_tree = MaskedPathTree(
        path_tree, 
        [PurePath('include/example')],
    )

    assert path_tree.has_path(example_variant_path)
    assert not masked_path_tree.has_path(example_variant_path)

    assert set(masked_path_tree.ls_dir(PurePath('include'))) == {PurePath('include/example2/')}

    sub_masked_path_tree = masked_path_tree.restrict_to_subdir(PurePath('include'))
    assert set(sub_masked_path_tree.files()) == {example_struct2_toml_path.relative_to(PurePath('include'))}

    sub_masked_path_tree2 = masked_path_tree.restrict_to_subdir(PurePath('include/example/something'))
    assert set(sub_masked_path_tree2.files()) == set()

def test_masked_path_tree_subdir_restriction() -> None:
    path_tree = EmulatedPathTree.from_lists(
        files=[
            'a/b/c.txt',
        ],
        dirs=[],
    )

    masked_path_tree = MaskedPathTree(
        path_tree, 
        [
            PurePath('include/example'),
            PurePath('include/example2'),
        ],
    )

    sub_masked_path_tree = masked_path_tree.restrict_to_subdir(PurePath('include'))
    assert sub_masked_path_tree.masked_out == frozenset([
        PurePath('example'),
        PurePath('example2'),
    ])

    sub_masked_path_tree2 = masked_path_tree.restrict_to_subdir(PurePath('include/example'))
    assert sub_masked_path_tree2.masked_out == frozenset([
        PurePath('.'),
    ])
    assert set(sub_masked_path_tree2.files()) == set()
