import pytest

from proj.unparse_project import (
    get_repo_rel_path,
    get_fullpath,
)
from proj.paths import (
    RoleInGroup,
    Repo,
    # LibraryRelPath,
    RepoRelPath,
    Library,
    FileGroup,
    File,
)
from pathlib import PurePath
from typing import (
    Any,
)
from proj.config_file import (
    ExtensionConfig,
)

# def test_get_library_rel_path() -> None:
#     p = File(FileGroup(PurePath('a/b')), Library('c'))
#

EXTENSION_CONFIG = ExtensionConfig(
    header_extension='.h',
    src_extension='.cc',
)

@pytest.mark.parametrize("input,correct", [
    # (
    #     LibraryRelPath(PurePath('a/b'), Library('c')),
    #     RepoRelPath(PurePath('lib/c/a/b'))
    # ),
    (
        File(FileGroup(PurePath('a/b'), Library('c')), RoleInGroup.DTGEN_TOML),
        RepoRelPath(PurePath('lib/c/include/c/a/b.dtg.toml'))
    ),
    (
        File(FileGroup(PurePath('a/b'), Library('c')), RoleInGroup.PUBLIC_HEADER),
        RepoRelPath(PurePath('lib/c/include/c/a/b.h'))
    ),
    (
        File(FileGroup(PurePath('a/b'), Library('c')), RoleInGroup.SOURCE),
        RepoRelPath(PurePath('lib/c/src/c/a/b.cc'))
    ),
    (
        File(FileGroup(PurePath('a/b'), Library('c')), RoleInGroup.GENERATED_HEADER),
        RepoRelPath(PurePath('lib/c/include/c/a/b.dtg.h'))
    ),
    (
        File(FileGroup(PurePath('a/b'), Library('c')), RoleInGroup.GENERATED_SOURCE),
        RepoRelPath(PurePath('lib/c/src/c/a/b.dtg.cc'))
    ),
    (
        File(FileGroup(PurePath('a/b'), Library('c')), RoleInGroup.TEST),
        RepoRelPath(PurePath('lib/c/test/src/c/a/b.cc'))
    ),
    (
        File(FileGroup(PurePath('a/b'), Library('c')), RoleInGroup.BENCHMARK),
        RepoRelPath(PurePath('lib/c/benchmark/src/c/a/b.cc'))
    ),
])
def test_get_repo_rel_path(input: Any, correct: RepoRelPath) -> None:
    result = get_repo_rel_path(input, EXTENSION_CONFIG)

    assert result == correct

@pytest.mark.parametrize("input,extension_config,correct", [
    (
        File(FileGroup(PurePath('a/b'), Library('c', Repo(PurePath('d')))), RoleInGroup.SOURCE),
        EXTENSION_CONFIG,
        PurePath('d/lib/c/src/c/a/b.cc'),
    )
])
def test_get_fullpath(input: Any, extension_config: ExtensionConfig, correct: PurePath) -> None:
    result = get_fullpath(input, extension_config)

    assert result == correct

