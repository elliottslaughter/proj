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
from .unparse_project import get_fullpath_for_file
from .config_file import ExtensionConfig
import re

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
        }

def get_file_group_info(
    file_group: FileGroup,
    ifndef_base: str,
    extension_config: ExtensionConfig,
) -> FileGroupInfo:
    return FileGroupInfo(
        public_header=get_fullpath_for_file(file_group.public_header, extension_config),
        generated_header=get_fullpath_for_file(file_group.generated_header, extension_config),
        generated_source=get_fullpath_for_file(file_group.generated_source, extension_config),
        source=get_fullpath_for_file(file_group.source, extension_config),
        test_source=get_fullpath_for_file(file_group.test, extension_config),
        benchmark_source=get_fullpath_for_file(file_group.benchmark, extension_config),
        toml_path=get_fullpath_for_file(file_group.dtgen_toml, extension_config),
        ifndef=get_ifndef_for_file_group_path(ifndef_base, file_group),
    )
