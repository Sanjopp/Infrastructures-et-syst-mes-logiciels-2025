from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class User:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    email: str | None = None
    auth_id: str | None = None

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"
