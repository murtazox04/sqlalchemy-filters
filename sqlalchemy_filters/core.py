from typing import Any, Dict, List, Type, Optional

from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_filters.filters import FilterSet
from sqlalchemy_filters.schema import create_filter_schema
from sqlalchemy_filters.utils import apply_ordering, apply_pagination
from sqlalchemy_filters.custom_filters import CustomFilterRegistry
from sqlalchemy_filters.typing import Model, Query


class SQLAlchemyFilter:
    def __init__(
        self,
        model: Type[Model],
        query: Query,
        filterset_class: Type[FilterSet],
        search_fields: List[str],
        order_fields: List[str],
        session: AsyncSession
    ):
        self.model = model
        self.query = query
        self.filterset = filterset_class(model)
        self.search_fields = search_fields
        self.order_fields = order_fields
        self.session = session
        self.schema = create_filter_schema(
            model, self.filterset.filters, search_fields, order_fields)
        self.custom_filter_registry = CustomFilterRegistry()

    async def filter(
        self,
        filters: Dict[str, Any],
        search: Optional[str] = None,
        order: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        query = self.query

        # Apply filters
        query = await self.filterset.filter(query, filters)

        # Apply search
        if search:
            query = self.filterset.search(query, search, self.search_fields)

        # Apply custom filters
        query = self.custom_filter_registry.apply_filters(query, filters)

        # Apply ordering
        if order:
            query = apply_ordering(query, order, self.order_fields, self.model)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)

        # Apply pagination
        query, pagination = apply_pagination(query, page, page_size)

        # Execute query
        result = await self.session.execute(query)

        return {
            "items": result.scalars().all(),
            "total": total,
            "pagination": pagination
        }

    def register_custom_filter(self, name: str, filter_func: callable):
        self.custom_filter_registry.register(name, filter_func)
