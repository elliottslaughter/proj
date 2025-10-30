from .trees.path_tree import PathTree
from pathlib import PurePath
from typing import (
    Iterator,
    Optional,
    TYPE_CHECKING,
    Union,
)
from .paths import (
    Repo,
    RepoRelPath,
    Library,
    LibraryRelPath,
    File,
    RoleInGroup,
    FileGroup,
)
from .utils import map_optional

if TYPE_CHECKING:
    from .config_file import ExtensionConfig

def _possible_config_paths(d: PurePath) -> Iterator[PurePath]:
    for _d in [d, *d.parents]:
        config_path = _d / ".proj.toml"
        yield config_path

def find_repo(p: PurePath, path_tree: PathTree) -> Optional[Repo]:
    return map_optional(parse_repo_path(p, path_tree), lambda repo_rel: repo_rel.repo)

def parse_repo_path(p: PurePath, path_tree: PathTree) -> Optional[RepoRelPath]:
    for possible_config in _possible_config_paths(p):
        if path_tree.has_file(possible_config):
            repo_root = possible_config.parent
            return RepoRelPath(p.relative_to(repo_root), Repo(repo_root))
    return None

def parse_library_path(repo_rel: RepoRelPath) -> LibraryRelPath:
    assert repo_rel.path.parts[0] == 'lib'
    library = Library(repo_rel.path.parts[1], repo_rel.repo)
    library_path = PurePath('lib') / library.name
    return LibraryRelPath(repo_rel.path.relative_to(library_path), library)

def find_libraries_in_repo(repo: Repo, path_tree: PathTree) -> Iterator[Library]:
    for lib_name in path_tree.ls_dir(repo.path / 'lib'):
        yield Library(lib_name.name, repo=repo)

def parse_file_path(
    rel: Union[LibraryRelPath, RepoRelPath], 
    extension_config: 'ExtensionConfig',
) -> Optional[File]:
    lib_rel: LibraryRelPath
    if isinstance(rel, LibraryRelPath):
        lib_rel = rel
    else:
        lib_rel = parse_library_path(rel)

    assert lib_rel.library is not None
    library = lib_rel.library
    p = lib_rel.path

    header_extension = extension_config.header_extension

    public_include_dir = PurePath('include') / library.name
    src_dir = PurePath('src') / library.name
    test_dir = PurePath('test/src') / library.name
    benchmark_dir = PurePath('benchmark/src') / library.name

    file_type: RoleInGroup
    group: FileGroup
    if p.is_relative_to(public_include_dir) and p.suffix == '.toml':
        pp = PurePath(p.stem)
        assert pp.suffix == '.dtg'
        file_type = RoleInGroup.DTGEN_TOML
        group = FileGroup(
            p.parent.relative_to(public_include_dir) / pp.stem,
            library,
        )
    elif p.is_relative_to(public_include_dir) and p.suffix == header_extension:
        pp = p.parent / p.stem
        if pp.suffix == '.dtg':
            file_type = RoleInGroup.GENERATED_HEADER
            group = FileGroup(
                p.parent.relative_to(public_include_dir) / pp.stem,
                library,
            )
        else:
            file_type = RoleInGroup.PUBLIC_HEADER
            group = FileGroup(
                p.parent.relative_to(public_include_dir) / p.stem,
                library,
            )

    elif p.is_relative_to(src_dir):
        pp = p.parent / p.stem
        if pp.suffix == '.dtg':
            file_type = RoleInGroup.GENERATED_SOURCE
            group = FileGroup(
                p.parent.relative_to(src_dir) / pp.stem,
                library,
            )
        else:
            file_type = RoleInGroup.SOURCE
            group = FileGroup(
                p.parent.relative_to(src_dir) / p.stem,
                library,
            )
    elif p.is_relative_to(test_dir):
        group=FileGroup(
            p.parent.relative_to(test_dir) / p.stem,
            library,
        )
        file_type=RoleInGroup.TEST
    elif p.is_relative_to(benchmark_dir):
        group=FileGroup(
            p.parent.relative_to(benchmark_dir) / p.stem,
            library,
        )
        file_type=RoleInGroup.BENCHMARK
    else:
        return None

    return File(
        group=group,
        role=file_type,
    )
