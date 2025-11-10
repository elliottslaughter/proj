from proj.dtgen.find_outdated import (
    find_outdated,
)
from proj.trees import (
    EmulatedPathTree,
    PathType,
)
from proj.paths import (
    RepoRelPath,
)
from proj.config_file import ExtensionConfig
from pathlib import PurePath

def test_find_outdated() -> None:
    repo_path_tree = EmulatedPathTree.from_map({
        PurePath(p): PathType.FILE 
        for p in [
            'CMakeLists.txt',
            '.proj.toml',
            'lib/CMakeLists.txt',
            'lib/person/CMakeLists.txt',
            'lib/person/include/person/example_struct.dtg.toml',
            'lib/person/include/person/example_enum.dtg.toml',
            'lib/person/include/person/example_variant.dtg.toml',
            'lib/person/include/person/out_of_date.dtg.hh',
            'lib/person/src/person/out_of_date2.dtg.cc',
        ]
    })

    extension_config = ExtensionConfig(
        '.hh',
        '.cc',
    )

    found = set(find_outdated(repo_path_tree, extension_config))
    correct = set([
        RepoRelPath(PurePath('lib/person/include/person/out_of_date.dtg.hh')),
        RepoRelPath(PurePath('lib/person/src/person/out_of_date2.dtg.cc')),
    ])
    assert found == correct

# def test_get_generated_source_path():
#     with project_instance('dtgen') as d:
#         correct = Path('lib/person/src/person/color.dtg.cc')
#         assert get_generated_source_path(d / 'lib/person/include/person/color.dtg.hh') == correct
#
# def test_get_nongenerated_source_path():
#     with project_instance('dtgen') as d:
#         correct = Path('lib/person/src/person/color.cc')
#         assert get_nongenerated_source_path(d / 'lib/person/include/person/color.dtg.hh') == correct
#
# def test_get_possible_spec_paths():
#     with project_instance('dtgen') as d:
#         found = set(get_possible_spec_paths(d / 'lib/person/include/person/color.dtg.hh'))
#         correct = set([
#             d / 'lib/person/include/person/color.struct.toml',
#             d / 'lib/person/include/person/color.enum.toml',
#             d / 'lib/person/include/person/color.variant.toml',
#             d / 'lib/person/src/person/color.struct.toml',
#             d / 'lib/person/src/person/color.enum.toml',
#             d / 'lib/person/src/person/color.variant.toml',
#         ])
#         assert found == correct


