from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class AuthUser:
    email: str
    password_hash: str
    name: str
    id: str = field(default_factory=lambda: str(uuid4()))
