import sys
from mock import Mock, MagicMock, call
sys.modules['browser'] = Mock()

import controller
from controller import Controller#, DIV
from reactive import Model


class DIV(object):
    def __init__(self, Id=None):
        self.id = Id


class A(Model):
    objects = {}

    def __init__(self, id, **kw):
        super(A, self).__init__(id, **kw)

filters = {}
filters['0'] = lambda x, y: {'__collection__': 'A', 'x': {"$gt": x, "$lt": y}}

filter = filters['0'](x=5, y=10)
m0 = A(id='0', x=0, y=3)
m1 = A(id='1', x=0, y=2)
m = A(id='2', x=0, y=1)


def test_index_in_list_empty():
    controller = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(), func=lambda: 5)
    controller.models = []
    ret = controller.indexInList(m)
    assert ret == (0, 'append')


def test_index_in_list_before():
    controller = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(), func=lambda: 5)
    controller.models = [m0]
    m = A(id='2', x=1, y=1)
    ret = controller.indexInList(m)
    assert ret == (0, 'before', '0')


def test_index_in_list_before0():
    controller = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(), func=lambda: 5)
    controller.models = [m0]
    m = A(id='2', x=0, y=3)
    ret = controller.indexInList(m)
    assert ret == (0, 'before', '0')


def test_index_in_list_after():
    controller = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(), func=lambda: 5)
    controller.models = [m0]
    m = A(id='2', x=-1, y=3)
    ret = controller.indexInList(m)
    assert ret == (1, 'after', '0')


def test_index_in_list_second_key_after_2():
    controller = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(), func=lambda: 5)
    controller.models = [m0, m1]
    ret = controller.indexInList(m)
    assert ret == (2, 'after', '1')


def test_new_append():
    ref = Mock()
    ref.append = Mock()
    jq = Mock(return_value=ref)
    controller.jq = jq
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '')
    m = A(id='2', x=0, y=3)
    controller_.new(m)
    assert ref.append.called
    assert controller_.models == [m]


def test_new__before():
    jq = Mock()
    before = jq().children().before

    controller.jq = jq
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '')
    m = A(id='2', x=0, y=3)
    controller_.models = [m]
    m2 = A(id='3', x=0, y=3)
    controller_.new(m2)

    jq.assert_called_with('#container')
    jq().children.assert_called_with("[reactive_id='2']")
    assert before.called
    assert controller_.models == [m2, m]


def test_new__first():
    jq = Mock()
    remove = jq().children().remove

    controller.jq = jq
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '', first=True)
    m = A(id='2', x=0, y=3)
    controller_.models = [m]
    m2 = A(id='3', x=0, y=3)
    controller_.new(m2)

    assert remove.called


def test_new__after():
    jq = Mock()
    after = jq().children().after

    controller.jq = jq
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '')
    m = A(id='2', x=0, y=3)
    controller_.models = [m]
    m2 = A(id='3', x=0, y=2)
    controller_.new(m2)

    jq.assert_called_with('#container')
    jq().children.assert_called_with("[reactive_id='2']")
    assert after.called
    assert controller_.models == [m, m2]


def test_new__after_first():
    jq = Mock()
    after = jq().children().after

    controller.jq = jq
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '', first=True)
    m = A(id='2', x=0, y=3)
    controller_.models = [m]
    m2 = A(id='3', x=0, y=2)
    controller_.new(m2)

    assert not after.called


def test_out_first():
    jq = Mock()
    children = jq().children

    controller.jq = jq
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '', first=True)
    m = A(id='2', x=0, y=3)
    controller_.models = [m]

    controller_.out(m)

    assert call("[reactive_id='2']") == children.mock_calls[0]
    assert children().remove.called
    assert controller_.models == []


def test_out_first_second_goes_to_first():
    jq = Mock()
    makeDIV_backup = controller.makeDIV
    makeDIV = Mock()

    controller.jq = jq
    controller.makeDIV = makeDIV
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '', first=True)
    m = A(id='2', x=0, y=3)
    m2 = A(id='3', x=0, y=2)
    controller_.models = [m, m2]

    controller_.out(m)
    controller.makeDIV = makeDIV_backup
    assert controller_.models == [m2]
    assert call("#container") == jq.mock_calls[-2]
    assert makeDIV.mock_calls[0] == call('3', m2, controller_.func)
    assert jq().append.called
    assert controller_.models == [m2]


def test_out_not_first():
    jq = Mock()

    controller.jq = jq
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '')
    m = A(id='2', x=0, y=3)
    controller_.models = [m]

    controller_.out(m)
    assert controller_.models == []


def test_out_not_first_more_than_one():
    jq = Mock()

    controller.jq = jq
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '')
    m = A(id='2', x=0, y=3)
    m2 = A(id='3', x=0, y=3)
    controller_.models = [m, m2]

    controller_.out(m)
    assert controller_.models == [m2]


def test_modify_when_second_pass_to_first():
    jq = Mock()
    children = jq().children

    controller.jq = jq
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '', first=True)
    m = A(id='2', x=0, y=3)
    m2 = A(id='3', x=0, y=2)
    controller_.models = [m, m2]
    m2.y = 4

    controller_.modify(m2)

    assert call("[reactive_id='2']") in children.mock_calls
    assert children().remove.called
    assert call("<div reactive_id='3'>test</div>") in jq.mock_calls
    assert controller_.models == [m2, m]


def test_modify_when_first_pass_to_second():
    jq = Mock()
    children = jq().children

    controller.jq = jq
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '', first=True)
    m = A(id='2', x=0, y=3)
    m2 = A(id='3', x=0, y=2)
    controller_.models = [m, m2]
    m.y = 1

    controller_.modify(m)

    assert call("[reactive_id='2']") in children.mock_calls
    assert children().remove.called
    assert call("<div reactive_id='3'>test</div>") in jq.mock_calls
    assert controller_.models == [m2, m]


def test_modify_when_move_to__after():
    jq = Mock()
    children = jq().children

    controller.jq = jq
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '')
    m = A(id='2', x=0, y=3)
    m2 = A(id='3', x=0, y=2)
    controller_.models = [m, m2]
    m.y = 1

    controller_.modify(m)

    assert call("[reactive_id='2']") == children.mock_calls[0]
    assert children().remove.called
    assert call("[reactive_id='3']") == children.mock_calls[2]
    assert children().after.called
    assert controller_.models == [m2, m]


def test_modify_when_move_to__before():
    jq = Mock()
    children = jq().children

    controller.jq = jq
    controller_ = Controller(key=[('x', 'desc'), ('y', 'desc')], filter=filter, node=DIV(Id='container'), func=lambda model, node: '')
    m = A(id='2', x=0, y=3)
    m2 = A(id='3', x=0, y=2)
    controller_.models = [m, m2]
    m2.y = 4

    controller_.modify(m2)

    assert call("[reactive_id='3']") == children.mock_calls[0]
    assert children().remove.called
    assert call("[reactive_id='2']") == children.mock_calls[2]
    assert children().before.called
    assert controller_.models == [m2, m]