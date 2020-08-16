from typ.types import char, NoneType
from pytest import *


def test_char():
    assert 'x' == char('x')


def test_char_too_long():
    with raises(ValueError):
        char('too long')
