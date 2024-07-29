# sqlalchemy-filters

`lib/sqlalchemy_filters/__init__.py`:
```py
from .services import FilterConfig, GenericFilterService, create_filter_model
```
`lib/sqlalchemy_filters/schema.py`:
```py
from pydantic import BaseModel, Field
from typing import Optional, Any, List


class Pagination(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class FilterOperator(BaseModel):
    eq: Optional[Any] = None
    ne: Optional[Any] = None
    gt: Optional[Any] = None
    ge: Optional[Any] = None
    lt: Optional[Any] = None
    le: Optional[Any] = None
    like: Optional[str] = None
    ilike: Optional[str] = None
    in_: Optional[List[Any]] = None
    not_in: Optional[List[Any]] = None
    is_null: Optional[bool] = None


class FilterField(BaseModel):
    field: str
    operator: FilterOperator


class OrderingField(BaseModel):
    field: str
    direction: str = "asc"

```
`lib/sqlalchemy_filters/filters.py`:
```py
from typing import Any, List, Type, Dict

from sqlalchemy.future import select
from sqlalchemy import Column, inspect, or_
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.sql.expression import cast

from .schema import FilterOperator, OrderingField


class FilterSet:
    model: Type[Any]
    fields: List[str] = []
    exclude: List[str] = []
    search_fields: List[str] = []
    ordering_fields: List[str] = []

    def __init__(self, **data):
        self.declared_filters: Dict[str, FilterOperator] = {}
        for key, value in data.items():
            setattr(self, key, value)
        self._populate_filters()

    def _populate_filters(self):
        if not self.fields and not self.exclude:
            self.fields = [c.key for c in inspect(self.model).columns]

        for field_name in self.fields:
            if field_name not in self.exclude:
                column = self._get_column(field_name)
                self.declared_filters[field_name] = self._create_filter(
                    field_name, column)

    def _get_column(self, field_name: str) -> Column:
        if "__" in field_name:
            parts = field_name.split("__")
            attr = getattr(self.model, parts[0])
            for part in parts[1:-1]:
                attr = getattr(attr.property.mapper.class_, part)
            return getattr(attr.property.mapper.class_, parts[-1])
        return getattr(self.model, field_name)

    def _create_filter(self, field_name: str, column: Column) -> FilterOperator:
        return FilterOperator()

    async def filter_queryset(self, session: AsyncSession, filter_data: dict):
        query = select(self.model)
        for field, value in filter_data.items():
            if field in self.declared_filters:
                filter_obj = self.declared_filters[field]
                query = await self._apply_filter(session, query, field, filter_obj, value)
        return query

    async def _apply_filter(self, session: AsyncSession, query, field: str, filter_obj: FilterOperator, value: Any):
        column = self._get_column(field)
        if isinstance(value, dict):
            for op, op_value in value.items():
                filter_operation = getattr(self, f"filter_{op}", None)
                if filter_operation:
                    query = await filter_operation(session, query, column, op_value)
        else:
            query = await self.filter_eq(session, query, column, value)
        return query

    async def filter_eq(self, session: AsyncSession, query, column, value):
        return query.filter(column == value)

    async def filter_ne(self, session: AsyncSession, query, column, value):
        return query.filter(column != value)

    async def filter_gt(self, session: AsyncSession, query, column, value):
        return query.filter(column > value)

    async def filter_ge(self, session: AsyncSession, query, column, value):
        return query.filter(column >= value)

    async def filter_lt(self, session: AsyncSession, query, column, value):
        return query.filter(column < value)

    async def filter_le(self, session: AsyncSession, query, column, value):
        return query.filter(column <= value)

    async def filter_like(self, session: AsyncSession, query, column, value):
        return query.filter(column.like(f"%{self._sanitize_like_value(value)}%"))

    async def filter_ilike(self, session: AsyncSession, query, column, value):
        return query.filter(column.ilike(f"%{self._sanitize_like_value(value)}%"))

    async def filter_in_(self, session: AsyncSession, query, column, value):
        return query.filter(column.in_(value))

    async def filter_not_in(self, session: AsyncSession, query, column, value):
        return query.filter(column.not_in(value))

    async def filter_is_null(self, session: AsyncSession, query, column, value):
        return query.filter(column.is_(None) if value else column.isnot(None))

    @staticmethod
    def _sanitize_like_value(value: str) -> str:
        return value.replace("%", r"\%").replace("_", r"\_")

    async def order_queryset(self, session: AsyncSession, query, ordering: List[OrderingField]):
        for order in ordering:
            if order.field in self.ordering_fields:
                column = self._get_column(order.field)
                if order.direction.lower() == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column)
        return query

    async def search_queryset(self, session: AsyncSession, query, search_term: str):
        if not self.search_fields:
            return query

        search_filters = []
        for field in self.search_fields:
            column = self._get_column(field)
            search_filters.append(column.ilike(
                f"%{self._sanitize_like_value(search_term)}%"))
        return query.filter(or_(*search_filters))
```
`lib/sqlalchemy_filters/services.py`:
```py
import logging
from pydantic import BaseModel, create_model
from typing import Any, List, Optional, Type, Tuple

from starlette.exceptions import HTTPException

from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .filters import FilterSet
from .schema import Pagination

logger = logging.getLogger(__name__)


class FilterConfig:
    def __init__(
            self,
            model: Type[Any],
            filter_class: Type[FilterSet],
            max_limit: int = 100
    ):
        self.model = model
        self.filter_class = filter_class
        self.max_limit = max_limit


def create_filter_query_params(filter_config):
    fields = {}
    filter_instance = filter_config.filter_class()

    for field in filter_instance.fields:
        fields[f"{field}__eq"] = (Optional[str], None)
        fields[f"{field}__ne"] = (Optional[str], None)
        fields[f"{field}__gt"] = (Optional[str], None)
        fields[f"{field}__ge"] = (Optional[str], None)
        fields[f"{field}__lt"] = (Optional[str], None)
        fields[f"{field}__le"] = (Optional[str], None)
        fields[f"{field}__like"] = (Optional[str], None)
        fields[f"{field}__ilike"] = (Optional[str], None)
        fields[f"{field}__in"] = (Optional[List[str]], None)
        fields[f"{field}__not_in"] = (Optional[List[str]], None)
        fields[f"{field}__is_null"] = (Optional[bool], None)

    # Add search and order_by fields
    fields["search"] = (Optional[str], None)
    fields["order_by"] = (Optional[List[str]], None)

    return fields


def create_filter_model(name: str, filter_config) -> Type[BaseModel]:
    fields = create_filter_query_params(filter_config)
    return create_model(f"{name}FilterModel", **fields)

    # def create_filter_model(name: str, filter_config):
    #     fields = {}
    #     filter_instance = filter_config.filter_class()
    #
    #     for field in filter_instance.fields:
    #         fields[field] = (Optional[FilterOperator], None)
    #
    #     fields["search"] = (Optional[str], None)
    #     fields["order_by"] = (Optional[List[OrderingField]], None)
    #
    #     return create_model(f"{name}FilterModel", **fields)


class GenericFilterService:
    def __init__(self, filter_config: FilterConfig):
        self.filter_config = filter_config
        self.model = filter_config.model
        self.filter_set = filter_config.filter_class()

    async def apply_filters(
            self,
            session: AsyncSession,
            filter_model: BaseModel,
            pagination: Pagination
    ) -> Tuple[List[Any], int]:
        filter_data = filter_model.model_dump(exclude_unset=True)
        search_term = filter_data.pop("search", None)
        ordering = filter_data.pop("order_by", None)

        query = await self.filter_set.filter_queryset(session, filter_data)

        if search_term:
            query = await self.filter_set.search_queryset(session, query, search_term)

        if ordering:
            query = await self.filter_set.order_queryset(session, query, ordering)

        total_count = await self.get_total_count(session, query)

        query = self._apply_pagination(query, pagination)

        result = await session.execute(query)
        items = result.scalars().all()

        return items, total_count

    def _apply_pagination(self, query, pagination: Pagination):
        if pagination.limit > self.filter_config.max_limit:
            raise ValueError(
                f"Maximum limit exceeded. Max allowed: {self.filter_config.max_limit}")
        return query.offset(pagination.offset).limit(pagination.limit)

    async def get_total_count(self, session: AsyncSession, query):
        try:
            count_query = select(func.count()).select_from(query.subquery())
            result = await session.execute(count_query)
            return result.scalar_one()
        except SQLAlchemyError as e:
            logger.error(f"Error occurred while getting total count: {str(e)}")
            raise HTTPException(
                status_code=500, detail="An error occurred while processing your request")
```

## Usage:
```py
from sqlalchemy_filters import AsyncFilterSet

from your_models import User


class UserFilter(AsyncFilterSet):
    model = User
    fields = ['username', 'email', 'age']
    search_fields = ['username', 'email']
    ordering_fields = ['username', 'age']

# In your API route or wherever you're using the filter
filter_config = AsyncFilterConfig(model=User, filter_class=UserFilter)
filter_service = AsyncGenericFilterService(filter_config)

# Use filter_service.apply_filters() in an async context
async def your_api_route(session: AsyncSession):
    filter_model = UserFilterModel(username=FilterOperator(eq="john"))
    pagination = Pagination(limit=10, offset=0)
    items, total_count = await filter_service.apply_filters(session, filter_model, pagination)
    # Process items and total_count as needed
```
