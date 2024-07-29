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
