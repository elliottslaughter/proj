from proj.trees.file_trees.traced_file_tree import (
    MutableTracedFileTreeByWrapping,
    MoveTrace,
    MkDirTrace,
    RmFileTrace,
    CreateFileTrace,
    ModifyFileTrace,
)
from proj.trees import EmulatedFileTree
from pathlib import PurePath

def test_mutable_traced_file_tree_by_wrapping() -> None:
    example_path = PurePath('my/example/path.txt')

    traced_file_tree = MutableTracedFileTreeByWrapping(
        EmulatedFileTree.from_lists(
            files=[
                (
                    example_path, 
                    '\n'.join([
                        'hello world',
                        '',
                        'goodbye world',
                        '',
                    ]),
                ),
            ],
            dirs=[]
        )
    )

    traced_file_tree.set_file_contents(
        example_path,
        '\n'.join([
            'something world',
            '',
            'goodbye',
            'world',
            '',
        ]),
    )

    result = traced_file_tree.get_file_trace()

    correct = [
        ModifyFileTrace(
            path=example_path, 
            diff='\n'.join([
                '@@ -1,3 +1,4 @@',
                '',
                '-hello world',
                '+something world',
                ' ',
                '-goodbye world',
                '+goodbye',
                '+world',
            ]),
        )
    ]

    assert result == correct
