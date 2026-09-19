import re
from typing import Self
from uuid import UUID, uuid4

from app.domain.entity import Entity
from app.domain.module import ModuleConfig, ModuleName


_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SLUG_MIN = 3
_SLUG_MAX = 40


class Project:
    def __init__(
        self,
        name: str,
        slug: str,
        *,
        project_id: UUID | None = None,
        entities: dict[str, Entity] | None = None,
        modules: dict[ModuleName, ModuleConfig] | None = None,
    ) -> None:
        self._validate_slug(slug)
        if not name or not name.strip():
            raise ValueError("project name must not be empty")
        self.id = project_id or uuid4()
        self.name = name.strip()
        self.slug = slug
        self.schema_name = f"proj_{slug.replace('-', '_')}"
        self._entities: dict[str, Entity] = entities or {}
        self._modules: dict[ModuleName, ModuleConfig] = modules or {}

    @staticmethod
    def _validate_slug(slug: str) -> None:
        if len(slug) < _SLUG_MIN or len(slug) > _SLUG_MAX:
            raise ValueError(
                f"slug must be {_SLUG_MIN}-{_SLUG_MAX} characters, got {len(slug)}"
            )
        if not _SLUG_PATTERN.match(slug):
            raise ValueError(
                f"invalid slug '{slug}': only [a-z0-9-], no leading/trailing/double hyphen"
            )

    @property
    def entities(self) -> dict[str, Entity]:
        return dict(self._entities)

    @property
    def modules(self) -> dict[ModuleName, ModuleConfig]:
        return dict(self._modules)

    def get_entity(self, name: str) -> Entity | None:
        return self._entities.get(name)

    def add_entity(self, entity: Entity) -> None:
        if entity.name in self._entities:
            raise ValueError(f"entity '{entity.name}' already exists")
        self._entities[entity.name] = entity

    def get_module(self, module: ModuleName) -> ModuleConfig | None:
        return self._modules.get(module)

    def enable_module(self, config: ModuleConfig) -> None:
        config.enabled = True
        self._modules[config.module] = config

    def to_dict(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "schema": self.schema_name,
            "modules": [m.value for m in self._modules if self._modules[m].enabled],
        }

    @classmethod
    def create(cls, name: str, slug: str) -> Self:
        project = cls(name=name, slug=slug)
        project.add_entity(Entity.user_with_default_pool())
        project.enable_module(ModuleConfig.default_auth())
        return project