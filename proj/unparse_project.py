from .paths import (
    File,
    LibraryRelPath,
    Library,
    RoleInGroup,
    RepoRelPath,
)
from .config_file import ExtensionConfig
from pathlib import PurePath
from typing import (
    Union,
    Optional,
)

def get_library_rel_path(file: File, extension_config: ExtensionConfig) -> LibraryRelPath:
    group_dir = file.group.group_path.parent
    group_name = file.group.group_path.name

    assert file.group is not None
    assert file.group.library is not None
    library = file.group.library
    library_name = file.group.library.name

    header_extension = extension_config.header_extension
    source_extension = extension_config.src_extension

    rel: PurePath
    if file.role == RoleInGroup.PUBLIC_HEADER:
        rel = PurePath('include') / library_name / group_dir / (group_name + header_extension)
    elif file.role == RoleInGroup.SOURCE:
        rel = PurePath('src') / library_name / group_dir / (group_name + source_extension)
    elif file.role == RoleInGroup.TEST:
        rel = PurePath('test/src') / library_name / group_dir / (group_name + source_extension)
    elif file.role == RoleInGroup.BENCHMARK:
        rel = PurePath('benchmark/src') / library_name / group_dir / (group_name + source_extension)
    elif file.role == RoleInGroup.DTGEN_TOML:
        rel = PurePath('include') / library_name / group_dir / (group_name + '.dtg.toml')
    elif file.role == RoleInGroup.GENERATED_HEADER:
        rel = PurePath('include') / library_name / group_dir / (group_name + '.dtg' + header_extension)
    elif file.role == RoleInGroup.GENERATED_SOURCE:
        rel = PurePath('src') / library_name / group_dir / (group_name + '.dtg' + source_extension)
    else:
        raise ValueError()

    return LibraryRelPath(rel, library)

def _get_repo_rel_path_for_file(file: File, extension_config: ExtensionConfig) -> RepoRelPath:
    library_rel_path = get_library_rel_path(file, extension_config)

    library = library_rel_path.library
    assert library is not None

    return RepoRelPath(PurePath('lib') / library.name / library_rel_path.path, library.repo)

def get_repo_rel_path(x: Union[File, LibraryRelPath, Library], extension_config: Optional[ExtensionConfig] = None) -> RepoRelPath:
    if isinstance(x, File):
        assert extension_config is not None
        return _get_repo_rel_path_for_file(x, extension_config)
    else:
        raise NotImplementedError()

def get_fullpath(x: Union[File, LibraryRelPath, Library, RepoRelPath], extension_config: Optional[ExtensionConfig] = None) -> PurePath:
    if isinstance(x, File):
        assert extension_config is not None
        return _get_fullpath_for_file(x, extension_config)
    elif isinstance(x, LibraryRelPath):
        return _get_fullpath_for_library_rel_path(x)
    elif isinstance(x, Library):
        return _get_fullpath_for_library(x)
    elif isinstance(x, RepoRelPath):
        return _get_fullpath_for_repo_rel_path(x)
    else:
        raise TypeError()

def _get_fullpath_for_file(file: File, extension_config: ExtensionConfig) -> PurePath:
    library_rel_path = get_library_rel_path(file, extension_config)
    return _get_fullpath_for_library_rel_path(library_rel_path)

def _get_fullpath_for_library_rel_path(lib_rel: LibraryRelPath) -> PurePath:
    assert lib_rel.library is not None
    return _get_fullpath_for_library(lib_rel.library) / lib_rel.path

def _get_fullpath_for_library(library: Library) -> PurePath:
    assert library.repo is not None
    return library.repo.path / 'lib' / library.name

def _get_fullpath_for_repo_rel_path(repo_rel: RepoRelPath) -> PurePath:
    assert repo_rel.repo is not None
    return repo_rel.repo.path / repo_rel.path
