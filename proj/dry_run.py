from .trees import (
    AllowMask,
    MutableTracedFileTreeByWrapping,
    MaskedPathTree,
    MaskedFileTree,
    EmulatedFileTree,
    FileTree,
    PathTree,
    EmulatedPathTree,
    MutableTracedPathTreeByWrapping,
)

def file_tree_to_emulated(tree: FileTree) -> EmulatedFileTree:
    return EmulatedFileTree.from_lists(
        files=[
            (f, tree.get_file_contents(f))
            for f in tree.files()
        ],
        dirs=[
            d for d in tree.dirs()    
        ],
    )

def path_tree_to_emulated(tree: PathTree) -> EmulatedPathTree:
    return EmulatedPathTree.from_lists(
        files=[f for f in tree.files()],
        dirs=[d for d in tree.dirs()],
    )


def load_repo_path_tree_for_dry_run(repo_path_tree: PathTree) -> MutableTracedPathTreeByWrapping:
    mask = AllowMask.from_iter([
        "lib/",
        "bin/",
    ])

    masked_path_tree = MaskedPathTree(
        repo_path_tree,
        mask,
    )

    return MutableTracedPathTreeByWrapping(
        path_tree_to_emulated(masked_path_tree),
    )


def load_repo_tree_for_dry_run(repo_file_tree: FileTree) -> MutableTracedFileTreeByWrapping:
    mask = AllowMask.from_iter([
        "lib/",
        "bin/",
    ])

    masked_path_tree = MaskedPathTree(
        repo_file_tree,
        mask,
    )

    masked_file_tree = MaskedFileTree(
        masked_path_tree,
        repo_file_tree,
    )

    return MutableTracedFileTreeByWrapping(
        file_tree_to_emulated(masked_file_tree),
    )

