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
