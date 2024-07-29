from typing import TypeVar, Any

from sqlalchemy import Select
from sqlalchemy.orm import DeclarativeMeta

Model = TypeVar('Model', bound=DeclarativeMeta)
Query = TypeVar('Query', bound=Select[Any])
