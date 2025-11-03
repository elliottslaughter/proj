from pathlib import PurePath
from .paths import (
    FileGroup,
    Library,
    File,
    RoleInGroup,
)
from typing import (
    Optional,
    Sequence,
    List,
)
from .utils import (
    with_suffix_removed,
)
import re
from dataclasses import dataclass
from proj.json import Json


@dataclass(frozen=True, order=True)
class IncludeSpec:
    path: PurePath
    system: bool

    def json(self) -> Json:
        return {
            "path": str(self.path),
            "system": self.system,
        }

@dataclass(frozen=True, order=True)
class SystemInclude:
    path: PurePath

@dataclass(frozen=True, order=True)
class UnknownInclude:
    path: PurePath


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

def get_include_path_for_file(file: File, header_extension: str) -> PurePath:
    match file.role:
        case RoleInGroup.PUBLIC_HEADER:
            return get_include_path(file.group, header_extension)
        case RoleInGroup.GENERATED_HEADER:
            return get_generated_include_path(file.group, header_extension)
        case _:
            raise ValueError()

def get_file_for_include_path(include_path: PurePath, header_extension: str) -> Optional[File]:
    if len(include_path.parts) <= 1:
        return None
    
    library_name = include_path.parts[0]
    library = Library(library_name)

    file_rel_path = include_path.relative_to(PurePath(library_name))

    if file_rel_path.name.endswith('.dtg' + header_extension):
        return FileGroup(
            with_suffix_removed(file_rel_path, n=2),
            library,
        ).generated_header
    elif file_rel_path.name.endswith(header_extension):
        return FileGroup(
            with_suffix_removed(file_rel_path, n=1),
            library,
        ).public_header
    else:
        return None

def find_include_specs_in_cpp_file_contents(contents: str, header_extension: str) -> Sequence[IncludeSpec]:
    def delimiter_is_system(delim: str) -> bool:
        assert delim in ['<', '"']
        return delim == '<'

    return [
        IncludeSpec(
            path=PurePath(m.group('include_path')),
            system=delimiter_is_system(m.group('delimiter')),
        )
        for m in re.finditer(r'#include\s+(?P<delimiter>[<"])(?P<include_path>\S+)[>"]', contents)
    ]

def find_includes_in_cpp_file_contents(contents: str, header_extension: str) -> Sequence[File | SystemInclude | UnknownInclude]:
    result: List[File | SystemInclude | UnknownInclude] = []
    for include_spec in find_include_specs_in_cpp_file_contents(contents, header_extension):
        if include_spec.system is False:
            file = get_file_for_include_path(include_spec.path, header_extension)
            if file is None:
                result.append(UnknownInclude(include_spec.path))
            else:
                result.append(file)
        else:
            result.append(SystemInclude(include_spec.path))
    return result
        
def replace_include_in_cpp_file_contents(contents: str, curr: PurePath, goal: PurePath) -> str:
    def do_replace(s: str, open_delim: str, close_delim: str) -> str:
        replaced, _ = re.subn(
            fr'#include(\s+){re.escape(open_delim)}{re.escape(str(curr))}{re.escape(close_delim)}', 
            fr'#include\1{open_delim}{str(goal)}{close_delim}',
            s,
        )
        return replaced

    contents = do_replace(contents, '"', '"')
    contents = do_replace(contents, '<', '>')
    return contents

def replace_file_group_include_in_cpp_file_contents(contents: str, curr: FileGroup, goal: FileGroup, header_extension: str) -> str:
    contents = replace_include_in_cpp_file_contents(
        contents, 
        curr=get_include_path(curr, header_extension=header_extension), 
        goal=get_include_path(goal, header_extension=header_extension),
    )
    
    contents = replace_include_in_cpp_file_contents(
        contents,
        curr=get_generated_include_path(curr, header_extension=header_extension),
        goal=get_generated_include_path(goal, header_extension=header_extension),
    )

    return contents

def replace_include_in_dtg_toml_file_contents(contents: str, curr: PurePath, goal: PurePath) -> str:
    result, _ = re.subn(fr'"{re.escape(str(curr))}"', f'"{goal}"', contents)
    return result

def replace_file_group_include_in_dtg_toml_file_contents(contents: str, curr: FileGroup, goal: FileGroup, header_extension: str) -> str:
    contents = replace_include_in_dtg_toml_file_contents(
        contents, 
        curr=get_include_path(curr, header_extension=header_extension), 
        goal=get_include_path(goal, header_extension=header_extension),
    )
    
    contents = replace_include_in_dtg_toml_file_contents(
        contents,
        curr=get_generated_include_path(curr, header_extension=header_extension),
        goal=get_generated_include_path(goal, header_extension=header_extension),
    )

    return contents
