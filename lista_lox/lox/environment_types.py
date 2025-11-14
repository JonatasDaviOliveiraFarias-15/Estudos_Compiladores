from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Any

Value = Any

@dataclass
class Env:
    values: dict[str, Value] = field(default_factory=dict)
    enclosing: Optional[Env] = None

    def push(self) -> Env:
        return Env(enclosing=self)

    def __getitem__(self, name: str) -> Value:
        if name in self.values:
            return self.values[name]
        if self.enclosing is not None:
            return self.enclosing[name]
        raise NameError(f"Variável não definida: {name}")
