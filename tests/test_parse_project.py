import pytest

from typing import (
    Union,
    Optional,
)
from proj.config_file import ExtensionConfig
from proj.paths import (
    RepoRelPath,
    File,
    FileGroup,
    RoleInGroup,
    LibraryRelPath,
    Library,
)
from pathlib import PurePath
from proj.parse_project import (
    parse_file_path,
)

EXTENSION_CONFIG = ExtensionConfig(
    header_extension='.h',
    src_extension='.cc',
)

@pytest.mark.parametrize("input,extension_config,correct", [
    (
        RepoRelPath(PurePath('lib/example/include/example/thing.dtg.toml')),
        EXTENSION_CONFIG,
        File(
            FileGroup(PurePath('thing'), Library('example')),
            RoleInGroup.DTGEN_TOML,
        ),
    ),
    (
        RepoRelPath(PurePath('lib/example/include/example/thing.dtg.h')),
        EXTENSION_CONFIG,
        File(
            FileGroup(PurePath('thing'), Library('example')),
            RoleInGroup.GENERATED_HEADER,
        ),
    ),
    (
        RepoRelPath(PurePath('lib/example/src/example/thing.dtg.cc')),
        EXTENSION_CONFIG,
        File(
            FileGroup(PurePath('thing'), Library('example')),
            RoleInGroup.GENERATED_SOURCE,
        ),
    ),
    (
        RepoRelPath(PurePath('lib/example/src/example/thing.cc')),
        EXTENSION_CONFIG,
        File(
            FileGroup(PurePath('thing'), Library('example')),
            RoleInGroup.SOURCE,
        ),
    ),
    (
        RepoRelPath(PurePath('lib/example/test/src/example/thing.cc')),
        EXTENSION_CONFIG,
        File(
            FileGroup(PurePath('thing'), Library('example')),
            RoleInGroup.TEST,
        ),
    ),
    (
        RepoRelPath(PurePath('lib/example/benchmark/src/example/thing.cc')),
        EXTENSION_CONFIG,
        File(
            FileGroup(PurePath('thing'), Library('example')),
            RoleInGroup.BENCHMARK,
        ),
    ),
])
def test_parse_file_path(
    input: Union[LibraryRelPath, RepoRelPath], 
    extension_config: ExtensionConfig, 
    correct: Optional[File],
) -> None:
    result = parse_file_path(input, extension_config)

    assert result == correct
