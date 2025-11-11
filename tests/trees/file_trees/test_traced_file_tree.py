from proj.trees.file_trees.traced_file_tree import (
    MutableTracedFileTreeByWrapping,
    ModifyFileTrace,
    MkDirTrace,
    CreateFileTrace,
)
from proj.trees import EmulatedFileTree
from pathlib import PurePath

def test_mutable_traced_file_tree_by_wrapping() -> None:
    example_path = PurePath('my/example/path.txt')

    old_contents = '\n'.join([
        'hello world',
        '',
        'goodbye world',
        '',
    ])

    traced_file_tree = MutableTracedFileTreeByWrapping(
        EmulatedFileTree.from_lists(
            files=[
                (
                    example_path, 
                    old_contents,
                ),
            ],
            dirs=[]
        )
    )

    new_contents = '\n'.join([
        'something world',
        '',
        'goodbye',
        'world',
        '',
    ])

    traced_file_tree.set_file_contents(
        example_path,
        new_contents,
        exist_ok=True,
    )
    traced_file_tree.mkdir(PurePath('does/not/exist'), exist_ok=True, parents=True)
    traced_file_tree.mkdir(PurePath('does/not/exist'), exist_ok=True, parents=True)
    traced_file_tree.set_file_contents(
        PurePath('still/does/not/exist/a.txt'),
        'bbbb',
        parents=True,
    )

    result = traced_file_tree.get_file_trace()

    correct = [
        ModifyFileTrace(
            path=example_path, 
            old_contents=old_contents,
            new_contents=new_contents,
        ),
        MkDirTrace(PurePath('does')),
        MkDirTrace(PurePath('does/not')),
        MkDirTrace(PurePath('does/not/exist')),
        MkDirTrace(PurePath('still')),
        MkDirTrace(PurePath('still/does')),
        MkDirTrace(PurePath('still/does/not')),
        MkDirTrace(PurePath('still/does/not/exist')),
        CreateFileTrace(
            PurePath('still/does/not/exist/a.txt'),
            'bbbb',
        )
    ]

    assert result == correct
