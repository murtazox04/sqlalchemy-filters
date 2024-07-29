import pytest

from sqlalchemy import select
from sqlalchemy_filters import Filter

from .conftest import User, UserFilterSet


@pytest.mark.asyncio
async def test_full_integration(async_session):
    query = select(User)
    filter = Filter(
        model=User,
        query=query,
        filterset_class=UserFilterSet,
        search_fields=['name'],
        order_fields=['name', 'age'],
        session=async_session
    )

    def custom_name_filter(query, value):
        return query.filter(User.name.ilike(f'%{value}%'))

    filter.register_custom_filter('custom_name', custom_name_filter)

    result = await filter.filter(
        filters={'age': 25, 'custom_name': 'al'},
        search='ice',
        order='-age',
        page=1,
        page_size=10
    )

    assert len(result['items']) == 1
    assert result['items'][0].name == 'Alice'
    assert result['total'] == 1
    assert result['pagination']['page'] == 1
    assert result['pagination']['page_size'] == 10
