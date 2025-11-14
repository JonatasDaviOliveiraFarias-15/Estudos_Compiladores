from dataclasses import dataclass, field
from typing import TypeVar, Generic, Dict, Optional

T = TypeVar("T")

@dataclass
class Env(Generic[T]):
    values: Dict[str, T] = field(default_factory=dict)
    enclosing: Optional['Env[T]'] = None

    def __setitem__(self, name: str, value: T) -> None:
        self.values[name] = value

    def assign(self, name: str, value: T) -> None:
        if name in self.values:
            self.values[name] = value
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)
        else:
            raise NameError(name)
        
    def __getitem__(self, name: str) -> T:
        if name in self.values:
            return self.values[name]
        if self.enclosing is not None:
            return self.enclosing[name]
        raise NameError(name)
    
    def push(self) -> 'Env[T]':
        return Env(enclosing=self)