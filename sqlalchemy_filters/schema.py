from pydantic import BaseModel, create_model, Field
from typing import Dict, Any, List, Optional, Type

from sqlalchemy_filters.typing import Model
from sqlalchemy_filters.filters import Filter


def create_filter_schema(
    model: Type[Model],
    filters: Dict[str, Filter],
    search_fields: List[str],
    order_fields: List[str]
) -> Type[BaseModel]:
    schema_fields: Dict[str, Any] = {}

    for field_name, filter_ in filters.items():
        field_type = getattr(model, filter_.field).type.python_type
        schema_fields[field_name] = (Optional[field_type], Field(default=None))

    schema_fields['search'] = (Optional[str], Field(default=None))
    schema_fields['order'] = (Optional[str], Field(default=None))
    schema_fields['page'] = (Optional[int], Field(default=1, ge=1))
    schema_fields['page_size'] = (
        Optional[int], Field(default=20, ge=1, le=100))

    return create_model(f'{model.__name__}FilterSchema', **schema_fields)
