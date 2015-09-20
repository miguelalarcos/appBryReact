import pytest
from tornado import gen
from DB import DB
from mock import MagicMock


@pytest.mark.gen_test
def test_1():
    @gen.coroutine
    def f(x):
        raise gen.Return({'x': 5})

    db = MagicMock()
    db['A'].find_one = f

    val = yield DB(db)['A'].find_one('0')
    assert val == {'__collection__': 'A', 'x': 5}
