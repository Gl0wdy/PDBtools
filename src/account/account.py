from dataclasses import dataclass
from typing import Any

@dataclass(slots=True)
class Account:
    name: str
    id: int
    cookies: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        return cls(
            name=data["name"],
            id=data["id"],
            cookies=data["cookies"],
        )
    
    def __repr__(self):
        return f'Account <{self.name}>'