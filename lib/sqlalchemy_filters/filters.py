from pydantic import BaseModel
from typing import Any, List, Type
from sqlalchemy.future import select
from sqlalchemy import Column, inspect, or_
from sqlalchemy.ext.asyncio import AsyncSession

from schema import FilterOperator, OrderingField


class FilterSet(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    model: Type[Any]
    fields: List[str] = []
    exclude: List[str] = []
    search_fields: List[str] = []
    ordering_fields: List[str] = []

    def __init__(self, **data):
        super().__init__(**data)
        self.declared_filters = {}
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
        for op, op_value in value.dict(exclude_unset=True).items():
            filter_operation = getattr(self, f"filter_{op}", None)
            if filter_operation:
                query = await filter_operation(session, query, column, op_value)
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
