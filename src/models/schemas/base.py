from typing import Callable, Self, Any

from pydantic import (
    BaseModel, SerializationInfo,
    model_serializer
)


class TelegraphyObj(BaseModel):
    ...
    

class TelegraphyObjExcludeNone(TelegraphyObj):
    
    @model_serializer(mode="wrap")
    def always_exclude_default(self, wrap: Callable[[Self], dict[str, Any]], info: SerializationInfo) -> dict[str, Any]:
        values = wrap(self)
        
        for key, value in values.copy().items():
            if isinstance(value, (int, float, bool)):
                continue
            if not value:
                del values[key]

        return values
