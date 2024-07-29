from typing import Dict, Any

from sqlalchemy_filters.typing import Query


class CustomFilterRegistry:
    def __init__(self):
        self.filters: Dict[str, callable] = {}

    def register(self, name: str, filter_func: callable):
        self.filters[name] = filter_func

    def apply_filters(self, query: Query, filter_data: Dict[str, Any]) -> Query:
        for name, value in filter_data.items():
            if name in self.filters:
                query = self.filters[name](query, value)
        return query
