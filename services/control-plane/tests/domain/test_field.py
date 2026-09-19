import pytest

from app.domain.field import Field, FieldType


def test_default_user_pool() -> None:
    pool = Field.default_user_pool()
    names = [f.name for f in pool]
    assert names == ["id", "email", "password", "fullName", "phone"]
    assert all(f.system for f in pool)
    email = next(f for f in pool if f.name == "email")
    assert email.unique is True
    assert email.field_type == FieldType.EMAIL


def test_valid_custom_field() -> None:
    f = Field("address", FieldType.STRING, required=False)
    assert f.name == "address"
    assert f.system is False
    assert f.to_dict() == {"name": "address", "type": "string", "system": False}


def test_invalid_field_name_starts_with_digit() -> None:
    with pytest.raises(ValueError, match="invalid field name"):
        Field("1bad", FieldType.STRING)


def test_invalid_field_name_special_char() -> None:
    with pytest.raises(ValueError, match="invalid field name"):
        Field("full-name", FieldType.STRING)


def test_enum_requires_values() -> None:
    with pytest.raises(ValueError, match="enum field requires enum_values"):
        Field("gender", FieldType.ENUM)


def test_enum_values_only_for_enum() -> None:
    with pytest.raises(ValueError, match="enum_values only allowed"):
        Field("name", FieldType.STRING, enum_values=["a"])


def test_enum_field_ok() -> None:
    f = Field("gender", FieldType.ENUM, enum_values=["male", "female"])
    d = f.to_dict()
    assert d["type"] == "enum"
    assert d["enumValues"] == ["male", "female"]