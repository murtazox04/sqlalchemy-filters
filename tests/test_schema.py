import pytest

from sqlalchemy_filters import create_filter_schema

from .conftest import User, UserFilterSet


def test_create_filter_schema():
    schema_class = create_filter_schema(
        User, UserFilterSet(User).filters, ['name'], ['name', 'age'])
    schema = schema_class()

    assert 'name' in schema.model_fields
    assert 'age' in schema.model_fields
    assert 'search' in schema.model_fields
    assert 'order' in schema.model_fields
    assert 'page' in schema.model_fields
    assert 'page_size' in schema.model_fields
