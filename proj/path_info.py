from dataclasses import dataclass
from pathlib import (
    Path,
    PurePath,
)
from .json import (
    Json,
)
from .paths import (
    File,
    FileGroup,
    Library,
    PathRole,
    LibraryRelPath,
    RepoRelPath,
    ExtensionConfig,
)
from typing import (
    Tuple,
    Optional,
)

@dataclass(frozen=True, order=True)
class HeaderInfo:
    path: Path
    ifndef: str

    def json(self) -> Json:
        return {
            "path": str(self.path),
            "ifndef": self.ifndef,
        }

@dataclass(frozen=True, order=True)
class PathInfo:
    generated_include: Path
    public_header: HeaderInfo
    generated_header: Path
    generated_source: Path
    header: Path
    source: Path
    test_source: Path
    benchmark_source: Path
    toml_path: Path

    def json(self) -> Json:
        return {
            "generated_include": str(self.generated_include),
            "public_header": self.public_header.json(),
            "generated_header": str(self.generated_header),
            "source": str(self.source),
            "generated_source": str(self.generated_source),
            "test_source": str(self.test_source),
            "benchmark_source": str(self.benchmark_source),
            "toml_path": str(self.toml_path),
        }

def get_library_for_path(path: RepoRelPath) -> Tuple[Library, LibraryRelPath]:
    assert path.raw.parts[0] == 'lib'
    library = Library(path.raw.parts[1])
    library_path = PurePath('lib') / library.name
    library_rel_path = LibraryRelPath(path.raw.relative_to(library_path))
    return (library, library_rel_path)

def get_library_and_file_for_path(path: RepoRelPath, extension_config: ExtensionConfig) -> Tuple[Library, File]:
    library, lib_rel_path = get_library_for_path(path)
    file = get_file_for_path(library, lib_rel_path, extension_config)
    return (library, file)

def get_file_for_path(library: Library, library_path: LibraryRelPath, extension_config: ExtensionConfig) -> Optional[File]:
    p = library_path.raw

    header_extension = extension_config.header_extension

    public_include_dir = PurePath('include') / library.name
    src_dir = PurePath('src') / library.name
    test_dir = PurePath('test/src') / library.name
    benchmark_dir = PurePath('benchmark/src') / library.name

    file_type: PathRole
    group: FileGroup
    if p.is_relative_to(public_include_dir) and p.suffix == '.toml':
        pp = p.parent / p.stem
        if pp.suffix == '.struct':
            file_type = PathRole.STRUCT_TOML
        elif pp.suffix == '.variant':
            file_type = PathRole.VARIANT_TOML
        elif pp.suffix == '.enum':
            file_type = PathRole.ENUM_TOML
        else:
            return None

        group = FileGroup(p.parent.relative_to(public_include_dir) / pp.stem)
    elif p.is_relative_to(public_include_dir) and p.suffix == header_extension:
        pp = p.parent / p.stem
        if pp.suffix == '.dtg':
            file_type = PathRole.GENERATED_HEADER
            group = FileGroup(p.parent.relative_to(public_include_dir) / pp.stem)
        else:
            file_type = PathRole.PUBLIC_HEADER
            group = FileGroup(p.parent.relative_to(public_include_dir) / p.stem)

    elif p.is_relative_to(src_dir):
        pp = p.parent / p.stem
        if pp.suffix == '.dtg':
            file_type = PathRole.GENERATED_SOURCE
        else:
            file_type = PathRole.SOURCE
        group = FileGroup(p.parent.relative_to(src_dir) / p.stem)
    elif p.is_relative_to(test_dir):
        group=FileGroup(p.parent.relative_to(test_dir) / p.stem)
        file_type=PathRole.TEST
    elif p.is_relative_to(benchmark_dir):
        group=FileGroup(p.parent.relative_to(benchmark_dir) / p.stem)
        file_type=PathRole.BENCHMARK
    else:
        return None

    return File(
        group=group,
        file_type=file_type,
    )


def get_file_group_for_path(library: Library, library_path: LibraryRelPath, extension_config: ExtensionConfig) -> FileGroup:
    return get_file_for_path(library, library_path, extension_config).group
