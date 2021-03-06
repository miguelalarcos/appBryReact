import sys
from mock import Mock, MagicMock, call
sys.modules['browser'] = Mock()

from ..static.controller import render, makeDIV
from ..static.reactive import Model, consume, execute
from ..static import controller


class A(Model):
    objects = {}


def test_1():
    node1 = Mock()
    node2 = Mock()
    jq = MagicMock()
    jq().find().__iter__.return_value = [node1, node2]

    controller.jq = jq

    node = jq()
    model = A(id=None, x=8, y=9)

    node1.html.return_value = '<span r>{x}</span>'
    node2.html.return_value = '<span r>{y}</span>'

    makeDIV('0', model, render, '<span r>{x}</span> <span r>{y}</span>')
    assert node.html.called
    assert call('<span r>8</span>') in node1.html.mock_calls
    assert call('<span r>9</span>') in node2.html.mock_calls
    assert model._dirty == set(['x', 'y'])

    model.x = 800
    assert len(execute) == 1
    consume()
    assert call('<span r>800</span>') in node1.html.mock_calls

