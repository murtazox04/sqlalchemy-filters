# sqlalchemy-filters

## Usage:
```bash
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
