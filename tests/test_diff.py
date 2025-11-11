from proj.diff import (
    render_path_diff,
    render_file_diff,
)
from proj.trees import (
    MoveTrace,
    MkDirTrace,
    RmFileTrace,
    CreateFileTrace,
    ModifyFileTrace,
)
from pathlib import PurePath
from typing import (
    List,
    Union,
)
import textwrap

def test_render_path_diff() -> None:
    path_diff: List[Union[MoveTrace, MkDirTrace, RmFileTrace]] = [
        MoveTrace(PurePath('a/b.txt'), PurePath('a/c.txt')),
        RmFileTrace(PurePath('q.txt')),
        MkDirTrace(PurePath('a/d')),
        MoveTrace(PurePath('a/c.txt'), PurePath('a/d/e.txt')),
        RmFileTrace(PurePath('a/a.txt')),
    ]

    result = render_path_diff(path_diff)
    correct = '''
    m a/{b.txt -> c.txt}
    d q.txt
    c a/d/
    m a/{c.txt -> d/e.txt}
    d a/a.txt
    '''

    assert result == textwrap.dedent(correct).strip() + '\n'

def test_render_file_diff() -> None:
    file_diff: List[Union[MoveTrace, MkDirTrace, RmFileTrace, CreateFileTrace, ModifyFileTrace]] = [
        MoveTrace(PurePath('a/b.txt'), PurePath('a/c.txt')),
        RmFileTrace(PurePath('q.txt')),
        MkDirTrace(PurePath('a/d')),
        CreateFileTrace(
            PurePath('a/f.txt'),
            '\n'.join([
                'a',
                'b',
                'c',
            ]),
        ),
        MoveTrace(PurePath('a/c.txt'), PurePath('a/d/e.txt')),
        RmFileTrace(PurePath('a/a.txt')),
        ModifyFileTrace(
            PurePath('a/f.txt'),
            '\n'.join([
                'a',
                'b',
                'c',
            ]),
            '\n'.join([
                'd',
                'e',
                'f',
            ]),
        ),
    ]

    result = render_file_diff(file_diff)

    correct = textwrap.dedent(
        '''
        m a/{b.txt -> c.txt}
        d q.txt
        c a/d/
        c a/f.txt
          a
          b
          c
        m a/{c.txt -> d/e.txt}
        d a/a.txt
        m a/f.txt
          @@ -1,3 +1,3 @@
          
          -a
          -b
          -c
          +d
          +e
          +f
        '''
    ).strip() + '\n'

    assert result == correct
