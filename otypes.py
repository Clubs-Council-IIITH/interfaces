import json
from functools import cached_property
from typing import Dict, List, Optional, Union

import strawberry
from strawberry.fastapi import BaseContext
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType

from models import CCRecruitment, Mails, PyObjectId, StorageFile


# custom context class
class Context(BaseContext):
    @cached_property
    def user(self) -> Union[Dict, None]:
        if not self.request:
            return None

        user = json.loads(self.request.headers.get("user", "{}"))
        return user

    @cached_property
    def cookies(self) -> Union[Dict, None]:
        if not self.request:
            return None

        cookies = json.loads(self.request.headers.get("cookies", "{}"))
        return cookies


# custom info type
Info = _Info[Context, RootValueType]

# serialize PyObjectId as a scalar type
PyObjectIdType = strawberry.scalar(
    PyObjectId, serialize=str, parse_value=lambda v: PyObjectId(v)
)


@strawberry.experimental.pydantic.type(model=Mails, fields=["subject", "uid"])
class MailReturnType:
    pass


@strawberry.experimental.pydantic.input(
    model=Mails, fields=["subject", "body", "to_recipients"]
)
class MailInput:
    cc_recipients: Optional[List[str]] = strawberry.UNSET
    uid: Optional[str] = strawberry.UNSET
    html_body: Optional[bool] = False


@strawberry.experimental.pydantic.input(
    model=CCRecruitment,
    # all_fields=True,
    fields=[
        "uid",
        "email",
        "teams",
        "design_experience",
        "why_this_position",
        "why_cc",
        "good_fit",
        "ideas",
        "other_bodies",
    ],
)
class CCRecruitmentInput:
    pass


@strawberry.experimental.pydantic.type(model=CCRecruitment, all_fields=True)
class CCRecruitmentType:
    pass


# signed url object type
@strawberry.type
class SignedURL:
    url: str

@strawberry.input
class SignedURLInput:
    static_file: bool = False
    filename: str | None = None

# StorageFile Types
@strawberry.experimental.pydantic.input(
    model=StorageFile, fields=["title", "url", "filetype"]
)
class StorageFileInput:
    pass


@strawberry.experimental.pydantic.type(model=StorageFile, all_fields=True)
class StorageFileType:
    pass


@strawberry.type
class StorageFilesReturn:
    _id: str
    title: str
