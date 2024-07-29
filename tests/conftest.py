import pytest
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy_filters import FilterSet, Filter

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)


class UserFilterSet(FilterSet):
    def __init__(self, model):
        super().__init__(model)
        self.add_filter('name', Filter('name', 'icontains'))
        self.add_filter('age', Filter('age', 'gte'))


@pytest.fixture(scope='session')
def engine():
    return create_async_engine('sqlite+aiosqlite:///:memory:', echo=True)


@pytest.fixture(scope='session')
async def async_session_factory(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        await session.execute(User.__table__.insert().values([
            {'name': 'Alice', 'age': 25},
            {'name': 'Bob', 'age': 30},
            {'name': 'Charlie', 'age': 35},
        ]))
        await session.commit()

    yield async_session


@pytest.fixture
async def async_session(async_session_factory):
    async with async_session_factory() as session:
        yield session
