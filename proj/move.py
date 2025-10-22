from dataclasses import dataclass
from .config_file import (
    ProjectConfig,
)
from pathlib import (
    Path,
)
from typing import (
    Set,
    Optional,
)
from proj.path_info import (
    get_path_role,
    PathRole,
    PathInfo,
    get_path_info,
)

@dataclass(frozen=True)
class ConcreteMove:
    src: Path
    dst: Path

def get_move_for_role(src_pathinfo: PathInfo, dst_pathinfo: PathInfo, role: PathRole) -> Optional[ConcreteMove]:
    src_path = src_pathinfo.path_for_role(role)
    dst_path = dst_pathinfo.path_for_role(role)

    if src_path is None:
        return None
    else:
        assert dst_path is not None
        return ConcreteMove(src_path, dst_path)

def get_move_plan(config: ProjectConfig, src: Path, dst: Path) -> Set[ConcreteMove]:
    src_pathinfo = get_path_info(src)
    dst_pathinfo = get_path_info(dst)

    assert get_path_role(src_pathinfo, src) == get_path_role(dst_pathinfo, dst)

    return {
        move for role in PathRole
        if (move := get_move_for_role(src_pathinfo, dst_pathinfo, role)) is not None
    }

def execute_move(config: ProjectConfig, src: Path, dst: Path) -> None:
    src_pathinfo = get_path_info(src)
    dst_pathinfo = get_path_info(dst)

    print(f'{src_pathinfo=}')
    print(f'{dst_pathinfo=}')
