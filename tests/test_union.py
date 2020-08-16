from typ.union import *


@union
class A:
    Number: int
    Text: str
    Unknown: None


@union
class B:
    Number: int
    Text: str
    Unknown: None


def test_is_tagged_union():
    assert isunion(A)
    assert not isunion(int)


def test_members():
    assert members(A) == {'Number': int, 'Text': str, 'Unknown': None}


def test_members_equality():
    assert A.Number(2) == A.Number(2)
    assert A.Number(2) != A.Number(3)
    assert A.Unknown() == A.Unknown()
    assert A.Unknown(None) == A.Unknown()


def test_creators_equality():
    assert A.Number == A.Number
    assert A.Number != B.Number
    assert A.Text != A.Number


def test_isinstance():
    assert isinstance(A.Text('something'), A)
    assert isinstance(A.Number(3), A)
    assert isinstance(A.Unknown(), A)


def test_ismember():
    assert ismember(A.Text('something'), A.Text)
    assert not ismember(A.Text('something'), A.Number)
    assert ismember(A.Unknown(), A.Unknown)


def test_member_name():
    assert member_name(A.Text('something')) == "Text"
    assert member_name(A.Number(3)) == "Number"
    assert member_name(A.Unknown()) == "Unknown"


def test_member_type():
    assert member_type(A.Text('something')) == str
    assert member_type(A.Number(3)) == int
    assert member_type(A.Unknown()) is None


def test_create_member():
    assert create_member(A, "Number", 3) == A.Number(3)
    assert create_member(A, "Unknown", None) == A.Unknown()


def test_member_value():
    a = A.Text('something')
    assert 'something' == a.value
    unknown = A.Unknown()
    assert unknown.value is None


def test_repr():
    assert repr(A.Text) == "A.Text of <class 'str'>"
    assert repr(A.Text('something')) == "A.Text('something')"
    assert repr(A.Unknown()) == "A.Unknown()"


def test_match_union():
    a = A.Text("something")
    result = match(a, {
        A.Text: lambda text: f'found: {text}',
    })
    assert result == "found: something"


def test_match_union_by_value():
    a = A.Text("something")
    result = match(a, {
        A.Text("something"): lambda text: f'something',
        A.Text: lambda text: f'not something'
    })
    assert result == "something"
    a = A.Text("not something")
    result = match(a, {
        A.Text("something"): lambda text: f'something',
        A.Text: lambda text: f'not something'
    })
    assert result == "not something"


def test_match_union_default():
    a = A.Number(3)
    result = match(a, {
        A.Text: lambda text: f'found: {text}',
        default: lambda: 'not found',
    })
    assert result == "not found"


def test_match_union_no_param():
    b = B.Unknown()
    result = b.match({
        B.Unknown: lambda _: 'unknown',
    })
    assert result == "unknown"
