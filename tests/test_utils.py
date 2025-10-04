from proj.utils import num_true

def test_num_true():
    assert num_true([False, True, False]) == 1
    assert num_true([False, False, False]) == 0
    assert num_true([]) == 0
    assert num_true([False, True, False, True]) == 2
