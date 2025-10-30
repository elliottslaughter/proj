from dataclasses import dataclass
from pathlib import (
    PurePath,
)
from .json import (
    Json,
)
from .paths import (
    FileGroup,
)
from .unparse_project import get_fullpath, get_repo_rel_path
from .config_file import ExtensionConfig, get_ifndef_for_path

@dataclass(frozen=True, order=True)
class FileGroupInfo:
    public_header: PurePath
    generated_header: PurePath
    generated_source: PurePath
    source: PurePath
    test_source: PurePath
    benchmark_source: PurePath
    toml_path: PurePath
    ifndef: str
    generated_include: PurePath
    include: PurePath

    def json(self) -> Json:
        return {
            "public_header": str(self.public_header),
            "generated_header": str(self.generated_header),
            "source": str(self.source),
            "generated_source": str(self.generated_source),
            "test_source": str(self.test_source),
            "benchmark_source": str(self.benchmark_source),
            "toml_path": str(self.toml_path),
            "ifndef": self.ifndef,
            "generated_include": str(self.generated_include),
            "include": str(self.include),
        }

def get_include_path(file_group: FileGroup, header_extension: str) -> PurePath:
    assert file_group.library is not None
    return (
        file_group.library.name 
        / file_group.group_path.parent 
        / (file_group.group_path.name + header_extension)
    )

def get_generated_include_path(file_group: FileGroup, header_extension: str) -> PurePath:
    assert file_group.library is not None
    return (
        file_group.library.name 
        / file_group.group_path.parent 
        / (file_group.group_path.name + '.dtg' + header_extension)
    )

def get_file_group_info(
    file_group: FileGroup,
    ifndef_base: str,
    extension_config: ExtensionConfig,
) -> FileGroupInfo:
    return FileGroupInfo(
        public_header=get_repo_rel_path(file_group.public_header, extension_config).path,
        generated_header=get_repo_rel_path(file_group.generated_header, extension_config).path,
        generated_source=get_repo_rel_path(file_group.generated_source, extension_config).path,
        source=get_repo_rel_path(file_group.source, extension_config).path,
        test_source=get_repo_rel_path(file_group.test, extension_config).path,
        benchmark_source=get_repo_rel_path(file_group.benchmark, extension_config).path,
        toml_path=get_repo_rel_path(file_group.dtgen_toml, extension_config).path,
        ifndef=get_ifndef_for_path(ifndef_base, get_repo_rel_path(file_group.public_header, extension_config)),
        generated_include=get_generated_include_path(file_group, extension_config.header_extension),
        include=get_include_path(file_group, extension_config.header_extension),
    )
