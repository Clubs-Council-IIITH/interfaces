import json
import strawberry

from strawberry.fastapi import BaseContext
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType

from typing import Union, Dict
from functools import cached_property

from models import PyObjectId


# custom context class
class Context(BaseContext):
    @cached_property
    def user(self) -> Union[Dict, None]:
        if not self.request:
            return None

        user = json.loads(self.request.headers.get("user", "{}"))
        return user


# custom info type
Info = _Info[Context, RootValueType]

# serialize PyObjectId as a scalar type
PyObjectIdType = strawberry.scalar(
    PyObjectId, serialize=str, parse_value=lambda v: PyObjectId(v)
)


# signed url object type
@strawberry.type
class SignedURL:
    url: str
