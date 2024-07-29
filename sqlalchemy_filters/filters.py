from typing import Dict, Any, Type, List

from sqlalchemy import and_, or_

from sqlalchemy_filters.utils import get_filter_operator
from sqlalchemy_filters.typing import Model, Query


class Filter:
    def __init__(self, field, lookup_type='exact'):
        self.field = field
        self.lookup_type = lookup_type

    async def filter(self, query: Query, value: Any) -> Query:
        op = get_filter_operator(self.lookup_type)
        return query.filter(op(getattr(self.model, self.field), value))


class FilterSet:
    def __init__(self, model: Type[Model]):
        self.model = model
        self.filters: Dict[str, Filter] = {}

    def add_filter(self, name: str, filter_: Filter):
        self.filters[name] = filter_

    async def filter(self, query: Query, filter_data: Dict[str, Any]) -> Query:
        filter_conditions = []
        for name, value in filter_data.items():
            if name in self.filters:
                filter_conditions.append(await self.filters[name].filter(query, value))
        return query.filter(and_(*filter_conditions))

    def search(self, query: Query, search_term: str, search_fields: List[str]) -> Query:
        search_filters = [getattr(self.model, field).ilike(
            f"%{search_term}%") for field in search_fields]
        return query.filter(or_(*search_filters))
