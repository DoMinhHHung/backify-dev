import pytest

from app.domain.module import ModuleName
from app.domain.project import Project


def test_create_project_seeds_user_and_auth() -> None:
    p = Project.create("Shop App", "shop-app")
    assert p.name == "Shop App"
    assert p.slug == "shop-app"
    assert p.schema_name == "proj_shop_app"
    assert p.get_entity("User") is not None
    auth = p.get_module(ModuleName.AUTH)
    assert auth is not None
    assert auth.enabled is True
    d = p.to_dict()
    assert d["modules"] == ["auth"]
    assert d["schema"] == "proj_shop_app"


def test_slug_too_short() -> None:
    with pytest.raises(ValueError, match="3-40"):
        Project.create("X", "ab")


def test_slug_invalid_chars() -> None:
    with pytest.raises(ValueError, match="invalid slug"):
        Project.create("X", "Shop_App")


def test_slug_double_hyphen() -> None:
    with pytest.raises(ValueError, match="invalid slug"):
        Project.create("X", "shop--app")


def test_empty_name() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        Project.create("  ", "shop-app")