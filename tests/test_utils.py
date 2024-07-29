from sqlalchemy import select

from sqlalchemy_filters.utils import get_filter_operator, apply_ordering
from .conftest import User


def test_get_filter_operator():
    eq_op = get_filter_operator('exact')
    assert eq_op(User.name, 'Alice').compare(User.name == 'Alice')

    contains_op = get_filter_operator('contains')
    assert contains_op(User.name, 'lic').compare(User.name.contains('lic'))


def test_apply_ordering():
    query = select(User)
    ordered_query = apply_ordering(query, 'name', ['name', 'age'], User)
    assert str(ordered_query) == str(query.order_by(User.name.asc()))

    ordered_query = apply_ordering(query, '-age', ['name', 'age'], User)
    assert str(ordered_query) == str(query.order_by(User.age.desc()))
