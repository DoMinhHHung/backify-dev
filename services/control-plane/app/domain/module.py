from enum import StrEnum


class ModuleName(StrEnum):
    AUTH = "auth"


class FunctionName(StrEnum):
    SIGNUP = "signup"
    SIGNIN = "signin"
    FORGOT_PASSWORD = "forgot_password"


class FunctionConfig:
    def __init__(
        self,
        function: FunctionName,
        enabled_fields: list[str] | None = None,
    ) -> None:
        self.function = function
        self._enabled_fields: set[str] = set(enabled_fields or [])

    @property
    def enabled_fields(self) -> list[str]:
        return sorted(self._enabled_fields)

    def is_enabled(self, field_name: str) -> bool:
        return field_name in self._enabled_fields

    def enable_field(self, field_name: str) -> None:
        self._enabled_fields.add(field_name)

    def disable_field(self, field_name: str) -> None:
        self._enabled_fields.discard(field_name)

    def to_dict(self) -> dict[str, object]:
        return {"enabledFields": self.enabled_fields}


class ModuleConfig:
    def __init__(
        self,
        module: ModuleName,
        *,
        enabled: bool = False,
        functions: dict[FunctionName, FunctionConfig] | None = None,
    ) -> None:
        self.module = module
        self.enabled = enabled
        self._functions: dict[FunctionName, FunctionConfig] = functions or {}

    def get_function(self, function: FunctionName) -> FunctionConfig | None:
        return self._functions.get(function)

    def set_function(self, config: FunctionConfig) -> None:
        self._functions[config.function] = config

    def to_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "functions": {
                fn.value: cfg.to_dict() for fn, cfg in self._functions.items()
            },
        }

    @classmethod
    def default_auth(cls) -> "ModuleConfig":
        signup = FunctionConfig(
            FunctionName.SIGNUP,
            enabled_fields=["email", "password", "fullName"],
        )
        signin = FunctionConfig(
            FunctionName.SIGNIN,
            enabled_fields=["email", "password"],
        )
        forgot = FunctionConfig(
            FunctionName.FORGOT_PASSWORD,
            enabled_fields=["email"],
        )
        return cls(
            ModuleName.AUTH,
            enabled=True,
            functions={
                FunctionName.SIGNUP: signup,
                FunctionName.SIGNIN: signin,
                FunctionName.FORGOT_PASSWORD: forgot,
            },
        )