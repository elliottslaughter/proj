from .trees import (
    MoveTrace,
    MkDirTrace,
    RmFileTrace,
    CreateFileTrace,
    ModifyFileTrace,
)
from typing import (
    Sequence,
    Union,
)
from .utils import (
    nearest_common_ancestor,
)
import io
import textwrap

def render_path_diff(
    path_diff: Sequence[Union[
        MoveTrace,
        MkDirTrace,
        RmFileTrace,
    ]],
) -> str:
    return render_file_diff(path_diff)

def render_file_diff(
    file_diff: Sequence[Union[
        MoveTrace,
        MkDirTrace,
        RmFileTrace,
        CreateFileTrace,
        ModifyFileTrace,
    ]],
) -> str:
    f = io.StringIO()
    for trace_elem in file_diff:
        match trace_elem:
            case MoveTrace(src, dst):
                ancestor = nearest_common_ancestor(src, dst)
                src_rel = src.relative_to(ancestor)
                dst_rel = dst.relative_to(ancestor)
                f.write(f'm {ancestor}/{{{src_rel} -> {dst_rel}}}\n')
            case MkDirTrace(path):
                f.write(f'c {path}/\n')
            case RmFileTrace(path):
                f.write(f'd {path}\n')
            case CreateFileTrace(path, content):
                f.write(f'c {path}\n' + textwrap.indent(content, '  ') + '\n') 
            case ModifyFileTrace(path):
                f.write(f'm {path}\n' + textwrap.indent(trace_elem.diff, '  ') + '\n') 
    return f.getvalue()
