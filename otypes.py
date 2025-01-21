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
    """
    Class provides user metadata and cookies from request headers, has methods for doing this.
    """

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


"""custom info Type for user metadata"""
Info = _Info[Context, RootValueType]

"""A scalar Type for serializing PyObjectId, used for id field"""
PyObjectIdType = strawberry.scalar(
    PyObjectId, serialize=str, parse_value=lambda v: PyObjectId(v)
)


@strawberry.experimental.pydantic.type(model=Mails, fields=["subject", "uid"])
class MailReturnType:
    """
    Type used for returning the subject and uid of a mail.
    """

    pass


@strawberry.experimental.pydantic.input(
    model=Mails, fields=["subject", "body", "to_recipients"]
)
class MailInput:
    """
    Input used for taking subject, body and to recipients of a mail.
    """

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
    """
    Input used for taking in answers of the recruitment form.
    """

    pass


@strawberry.experimental.pydantic.type(model=CCRecruitment, all_fields=True)
class CCRecruitmentType:
    """
    Type used for returning the answers of the recruitment form.
    """

    pass


# signed url object type
@strawberry.type
class SignedURL:
    """
    Type used for returning the signed url of a file.
    """

    url: str


@strawberry.input
class SignedURLInput:
    """
    Input used for taking details regarding size, name and format of a file.
    """

    static_file: bool = False
    filename: str | None = None
    max_size_mb: float = 0.3


# StorageFile Types
@strawberry.experimental.pydantic.input(
    model=StorageFile, fields=["title", "filename", "filetype"]
)
class StorageFileInput:
    """
    Input used for taking details regarding the file's title, name and type.
    """

    pass


@strawberry.experimental.pydantic.type(model=StorageFile, all_fields=True)
class StorageFileType:
    """
    Input used for taking all the details regarding the file.
    """

    pass
