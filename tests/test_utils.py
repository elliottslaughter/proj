import pytest
from proj.utils import (
    num_true,
    saturating_relative_to,
)
from pathlib import PurePath

def test_num_true() -> None:
    assert num_true([False, True, False]) == 1
    assert num_true([False, False, False]) == 0
    assert num_true([]) == 0
    assert num_true([False, True, False, True]) == 2

@pytest.mark.parametrize('child,parent,correct', [
    ('a/b', 'a/', 'b/'),
    ('a/', 'a/b/', '.'),
    ('a/', 'a/b/c/d/e', '.'),
    ('a/', 'a/', '.'),
])
def test_saturating_relative_to(child: str, parent: str, correct: str) -> None:
    assert saturating_relative_to(PurePath(child), PurePath(parent)) == PurePath(correct)
