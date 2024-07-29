from sqlalchemy import select
from sqlalchemy_filters import CustomFilterRegistry

from .conftest import User


def test_custom_filter_registry():
    registry = CustomFilterRegistry()

    def custom_age_filter(query, value):
        return query.filter(User.age.between(value - 5, value + 5))

    registry.register('age_range', custom_age_filter)

    query = select(User)
    filtered_query = registry.apply_filters(query, {'age_range': 30})

    assert str(filtered_query) != str(query)
    assert 'BETWEEN' in str(filtered_query)
    assert '25' in str(filtered_query) and '35' in str(filtered_query)
