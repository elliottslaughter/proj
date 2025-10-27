import pytest
from proj.paths import (
    ExtensionConfig,
    PathRole,
    File,
    FileGroup,
    LibraryRelPath,
    Library,
    RepoRelPath,
)
from pathlib import PurePath
from proj.path_info import (
    get_file_for_path,
    get_library_for_path,
)

EXTENSION_CONFIG = ExtensionConfig(
    '.h',
    '.cc',
)

def test_get_library_for_path() -> None:
    path = RepoRelPath(PurePath('lib/mylib/test/src/mylib/hello.cc'))

    result = get_library_for_path(path)
    correct = (
        Library('mylib'),
        LibraryRelPath(PurePath('test/src/mylib/hello.cc')),
    )

    assert result == correct

@pytest.mark.parametrize("lib_rel_path,correct", [
    (
        'include/mylib/something.h', 
        File(
            FileGroup(PurePath('something')),
            PathRole.PUBLIC_HEADER,
        )
    ), 
    (
        'include/mylib/abcde.dtg.h', 
        File(
            FileGroup(PurePath('abcde')),
            PathRole.GENERATED_HEADER,
        )
    ), 
])
def test_get_file_for_path(lib_rel_path: str, correct: File) -> None:
    assert get_file_for_path(
        Library('mylib'),
        LibraryRelPath(PurePath(lib_rel_path)),
        EXTENSION_CONFIG,
    ) == correct
