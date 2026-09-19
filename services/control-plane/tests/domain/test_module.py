from app.domain.module import (
    FunctionConfig,
    FunctionName,
    ModuleConfig,
    ModuleName,
)


def test_default_auth() -> None:
    m = ModuleConfig.default_auth()
    assert m.module == ModuleName.AUTH
    assert m.enabled is True
    signup = m.get_function(FunctionName.SIGNUP)
    assert signup is not None
    assert "email" in signup.enabled_fields
    assert "password" in signup.enabled_fields
    signin = m.get_function(FunctionName.SIGNIN)
    assert signin is not None
    assert signin.enabled_fields == ["email", "password"]


def test_toggle_field() -> None:
    cfg = FunctionConfig(FunctionName.SIGNUP, enabled_fields=["email"])
    cfg.enable_field("address")
    assert cfg.is_enabled("address")
    cfg.disable_field("address")
    assert not cfg.is_enabled("address")