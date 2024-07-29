# SQLAlchemy Filters

SQLAlchemy Filters is a powerful and flexible package for filtering SQLAlchemy queries in Python applications. It provides an easy-to-use interface for creating dynamic filters, supporting async operations, and allowing for custom filter implementations.

## Features

- Asynchronous support for modern Python applications
- Dynamic filter creation based on SQLAlchemy models
- Custom filter support for complex filtering scenarios
- Integration with Pydantic for request validation
- Ordering and pagination support
- Search functionality across multiple fields

## Installation

You can install SQLAlchemy Filters using pip:

```bash
pip install sqlalchemy-filters
```

## Requirements

- Python 3.6+
- SQLAlchemy 2.0+
- Pydantic 2.8+
- Starlette 0.37+

## Usage

Here's a quick example of how to use SQLAlchemy Filters:

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy_filters import SQLAlchemyFilter, FilterSet, Filter

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

async def main():
    engine = create_async_engine("sqlite+aiosqlite:///example.db")
    async with AsyncSession(engine) as session:
        query = select(User)
        user_filter = SQLAlchemyFilter(
            model=User,
            query=query,
            filterset_class=UserFilterSet,
            search_fields=['name'],
            order_fields=['name', 'age'],
            session=session
        )

        results = await user_filter.filter(
            filters={'name': 'John', 'age': 25},
            search='Doe',
            order='age',
            page=1,
            page_size=20
        )

        print(results)

# Run the async function
import asyncio
asyncio.run(main())
```

## Advanced Usage

### Custom Filters

You can create custom filters for more complex filtering scenarios:

```python
def custom_age_filter(query, value):
    return query.filter(User.age.between(value - 5, value + 5))

user_filter.register_custom_filter('age_range', custom_age_filter)

results = await user_filter.filter(filters={'age_range': 30})
```

### Extending FilterSet

You can extend the FilterSet class to create reusable filter configurations:

```python
class AdvancedUserFilterSet(FilterSet):
    def __init__(self, model):
        super().__init__(model)
        self.add_filter('name', Filter('name', 'icontains'))
        self.add_filter('age_min', Filter('age', 'gte'))
        self.add_filter('age_max', Filter('age', 'lte'))

    async def filter(self, query, filter_data):
        query = await super().filter(query, filter_data)
        if 'premium' in filter_data:
            query = query.filter(User.is_premium == filter_data['premium'])
        return query

user_filter = SQLAlchemyFilter(
    model=User,
    query=query,
    filterset_class=AdvancedUserFilterSet,
    search_fields=['name', 'email'],
    order_fields=['name', 'age', 'created_at'],
    session=session
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Author

Murtazo Khurramov (murtazox04@gmail.com)

## Links

- GitHub: https://github.com/murtazox04/sqlalchemy-filters
- PyPI: [Link to be added when package is published]

