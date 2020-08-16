__UNION_MEMBERS__ = "__union_members"


def union(union_class):
    class UnionMember(union_class):
        def __init__(self, member_name, member_type, value):
            self._member_name = member_name
            self._member_type = member_type
            self.value = value
            if member_type is not None:
                self._args = (value,)
            else:
                self._args = ()

        def __eq__(self, other):
            if not isinstance(other, self.__class__):
                return False
            return (self._member_name, self.value) == (other._member_name, other.value)

        def __repr__(self):
            if '__repr__' in vars(union_class):
                rep = union_class.__repr__(self)
            else:
                if self._member_type is None:
                    rep = f'{union_class.__name__}.{self._member_name}()'
                else:
                    rep = f'{union_class.__name__}.{self._member_name}({repr(self.value)})'
            return rep

        def __hash__(self):
            return hash((self._member_name, self.value))

        def match(self, cases):
            return match(self, cases)

    class UnionMemberCreator:
        def __init__(self, union_type, member_name, member_type):
            self._union_type = union_type
            self._member_name = member_name
            self._member_type = member_type

        def __call__(self, *args):
            if self._member_type is None:
                assert len(args) == 0 or len(args) == 1
                if len(args) == 1:
                    assert args[0] is None
                return UnionMember(self._member_name, self._member_type, None)
            else:
                assert len(args) == 1
                arg = args[0]
                assert isinstance(arg, self._member_type)
                return UnionMember(self._member_name, self._member_type, arg)

        def __eq__(self, other):
            if not isinstance(other, UnionMemberCreator):
                return False
            return other._union_type == self._union_type and other._member_name == self._member_name

        def __repr__(self):
            return f'{self._union_type.__name__}.{self._member_name} of {repr(self._member_type)}'

        def __hash__(self):
            return hash(self._member_name)

    union_members = union_class.__dict__.get('__annotations__', {})

    for name, typ in union_members.items():
        setattr(union_class, name, UnionMemberCreator(union_class, name, typ))

    setattr(union_class, __UNION_MEMBERS__, union_members)

    return union_class


def create_member(typ, member_name, arg=None):
    if members(typ)[member_name] is None:
        return getattr(typ, member_name)()
    else:
        return getattr(typ, member_name)(arg)


def isunion(klass):
    return hasattr(klass, __UNION_MEMBERS__)


def members(klass):
    if not hasattr(klass, __UNION_MEMBERS__):
        raise TypeError(f'{klass} is not tagged union')
    return getattr(klass, __UNION_MEMBERS__)


def _isinstance_member_creator(member):
    return member.__class__.__name__ == "UnionMemberCreator"


def _isinstance_member(member):
    return member.__class__.__name__ == "UnionMember"


def ismember(value, member_creator):
    if not _isinstance_member_creator(member_creator):
        raise ValueError(f'{member_creator} is not member creator')
    return isinstance(value, member_creator._union_type) and value._member_name == member_creator._member_name


def member_name(obj):
    if not _isinstance_member(obj):
        raise ValueError(f'{obj} is not tagged_union member')
    return obj._member_name


def member_type(obj):
    if not _isinstance_member(obj):
        raise ValueError(f'{obj} is not tagged_union member')
    return obj._member_type


default = object()


def _match_case(case_key, obj):
    if default == case_key:
        return True
    if _isinstance_member_creator(case_key):
        return ismember(obj, case_key)
    else:
        return case_key == obj


def match(obj, cases):
    case_key, case_lambda = next(((case_key, case_lambda) for case_key, case_lambda in cases.items() if _match_case(case_key, obj)), (None, None))
    if case_lambda is None:
        raise ValueError(f'{obj} was not matched by any case')
    if case_key == default:
        return case_lambda()
    else:
        return case_lambda(obj.value)
