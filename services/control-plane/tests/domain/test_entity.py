import pytest

from app.domain.entity import Entity
from app.domain.field import Field, FieldType


def test_user_with_default_pool() -> None:
    e = Entity.user_with_default_pool()
    assert e.name == "User"
    assert e.has_field("email")
    assert len(e.fields) == 5


def test_add_and_remove_custom_field() -> None:
    e = Entity.user_with_default_pool()
    e.add_field(Field("address", FieldType.STRING))
    assert e.has_field("address")
    removed = e.remove_field("address")
    assert removed.name == "address"
    assert not e.has_field("address")


def test_cannot_remove_system_field() -> None:
    e = Entity.user_with_default_pool()
    with pytest.raises(ValueError, match="cannot remove system field"):
        e.remove_field("email")


def test_duplicate_field() -> None:
    e = Entity.user_with_default_pool()
    with pytest.raises(ValueError, match="already exists"):
        e.add_field(Field("email", FieldType.EMAIL))


def test_invalid_entity_name() -> None:
    with pytest.raises(ValueError, match="invalid entity name"):
        Entity("123Bad")