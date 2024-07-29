import pytest

from sqlalchemy import select
from sqlalchemy_filters import SQLAlchemyFilter

from .conftest import User, UserFilterSet


@pytest.mark.asyncio
async def test_filter_by_name(async_session):
    query = select(User)
    filter = SQLAlchemyFilter(
        model=User,
        query=query,
        filterset_class=UserFilterSet,
        search_fields=['name'],
        order_fields=['name', 'age'],
        session=async_session
    )

    result = await filter.filter(filters={'name': 'ali'})
    assert len(result['items']) == 1
    assert result['items'][0].name == 'Alice'


@pytest.mark.asyncio
async def test_filter_by_age(async_session):
    query = select(User)
    filter = SQLAlchemyFilter(
        model=User,
        query=query,
        filterset_class=UserFilterSet,
        search_fields=['name'],
        order_fields=['name', 'age'],
        session=async_session
    )

    result = await filter.filter(filters={'age': 30})
    assert len(result['items']) == 2
    assert all(user.age >= 30 for user in result['items'])


@pytest.mark.asyncio
async def test_search(async_session):
    query = select(User)
    filter = SQLAlchemyFilter(
        model=User,
        query=query,
        filterset_class=UserFilterSet,
        search_fields=['name'],
        order_fields=['name', 'age'],
        session=async_session
    )

    result = await filter.filter(search='char')
    assert len(result['items']) == 1
    assert result['items'][0].name == 'Charlie'


@pytest.mark.asyncio
async def test_ordering(async_session):
    query = select(User)
    filter = SQLAlchemyFilter(
        model=User,
        query=query,
        filterset_class=UserFilterSet,
        search_fields=['name'],
        order_fields=['name', 'age'],
        session=async_session
    )

    result = await filter.filter(order='-age')
    assert len(result['items']) == 3
    assert [user.age for user in result['items']] == [35, 30, 25]
