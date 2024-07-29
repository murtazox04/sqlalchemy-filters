from sqlalchemy import asc, desc
from sqlalchemy.sql import operators
from typing import Dict, Tuple, List, Type

from sqlalchemy_filters.typing import Model, Query


def get_filter_operator(lookup_type: str):
    op_map = {
        'exact': operators.eq,
        'iexact': lambda c, v: c.ilike(v),
        'contains': lambda c, v: c.contains(v),
        'icontains': lambda c, v: c.ilike(f'%{v}%'),
        'in': operators.in_op,
        'gt': operators.gt,
        'gte': operators.ge,
        'lt': operators.lt,
        'lte': operators.le,
        'startswith': lambda c, v: c.startswith(v),
        'istartswith': lambda c, v: c.ilike(f'{v}%'),
        'endswith': lambda c, v: c.endswith(v),
        'iendswith': lambda c, v: c.ilike(f'%{v}'),
        'range': lambda c, v: operators.and_(c >= v[0], c <= v[1]),
        'isnull': lambda c, v: c.is_(None) if v else c.isnot(None),
    }
    return op_map.get(lookup_type, operators.eq)


def apply_ordering(query: Query, order: str, order_fields: List[str], model: Type[Model]) -> Query:
    if order.startswith('-'):
        field = order[1:]
        direction = desc
    else:
        field = order
        direction = asc

    if field in order_fields:
        return query.order_by(direction(getattr(model, field)))
    return query


def apply_pagination(query: Query, page: int, page_size: int) -> Tuple[Query, Dict[str, int]]:
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size), {"page": page, "page_size": page_size}
