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
    Class provides user metadata and cookies from request headers, has
    methods for doing this.
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


Info = _Info[Context, RootValueType]
"""custom info Type for user metadata"""

PyObjectIdType = strawberry.scalar(
    PyObjectId, serialize=str, parse_value=lambda v: PyObjectId(v)
)
"""A scalar Type for serializing PyObjectId, used for id field"""


@strawberry.experimental.pydantic.type(model=Mails)
class MailReturnType:
    """
    Type used for returning the subject and uid of a mail.

    Attributes:
        uid (str): UID of the sender.
        subject (str): Subject of the mail.
    """

    uid: strawberry.auto
    subject: strawberry.auto


@strawberry.experimental.pydantic.input(model=Mails)
class MailInput:
    """
    Input used for taking subject, body and to recipients of a mail.

    Attributes:
        subject (str): Subject of the mail.
        body (str): Body of the mail.
        to_recipients (List[str]): List of to recipients.
        cc_recipients (Optional[List[str]]): List of CC recipients.
                                        Defaults to None.
        uid (Optional[str]): UID of the sender. Defaults to None.
        html_body (Optional[bool]): Whether the body is in HTML format.
                                Defaults to False
    """

    subject: strawberry.auto
    body: strawberry.auto
    to_recipients: strawberry.auto
    cc_recipients: Optional[List[str]] = strawberry.UNSET
    uid: Optional[str] = strawberry.UNSET
    html_body: Optional[bool] = False


@strawberry.experimental.pydantic.input(model=CCRecruitment)
class CCRecruitmentInput:
    """
    Input used for taking in answers of the recruitment form.

    Attributes:
        uid (str): User ID of the applicant.
        email (str): Email of the applicant.
        teams (List[models.Team]): List of teams the applicant is applying for.
        design_experience (str): Design experience of the applicant. Defaults
                                to None.
        why_this_position (str): Why the applicant wants this position.
        why_cc (str): Why the applicant wants to join CC.
        ideas1 (str): Reasons for not participating in an event.
        ideas (str): Ideas the applicant has for CC.
        other_bodies (str | None): Other bodies the applicant is a part of.
                                Defaults to None.
        good_fit (str): Why the applicant is a good fit for CC.
    """

    uid: strawberry.auto
    email: strawberry.auto
    teams: strawberry.auto
    design_experience: strawberry.auto
    why_this_position: strawberry.auto
    why_cc: strawberry.auto
    ideas1: strawberry.auto
    ideas: strawberry.auto
    other_bodies: strawberry.auto
    good_fit: strawberry.auto


@strawberry.experimental.pydantic.type(model=CCRecruitment, all_fields=True)
class CCRecruitmentType:
    """
    Type used for returning the answers of the recruitment form.

    Attributes:
        fields (models.CCRecruitment): All fields of the CCRecruitment model.
    """

    pass


# signed url object type
@strawberry.type
class SignedURL:
    """
    Type used for returning the signed url of a file.

    Attributes:
        url (str): The signed URL.
    """

    url: str


@strawberry.input
class SignedURLInput:
    """
    Input used for taking details regarding size, name and format of a file.

    Attributes:
        static_file (bool): Whether the file is static or not.
                         Defaults to False.
        filename (str): Name of the file. Defaults to None.
        max_size_mb (float): Size of the file in MB. Defaults to 0.3.
    """

    static_file: bool = False
    filename: str | None = None
    max_size_mb: float = 0.3


# StorageFile Types
@strawberry.experimental.pydantic.input(model=StorageFile)
class StorageFileInput:
    """
    Input used for taking details regarding the file's title, name and type.

    Attributes:
        title (str): Title of the file.
        filename (str): Name of the file.
        filetype (str): Type of the file.
    """

    title: strawberry.auto
    filename: strawberry.auto
    filetype: strawberry.auto


@strawberry.experimental.pydantic.type(model=StorageFile, all_fields=True)
class StorageFileType:
    """
    Input used for taking all the details regarding the file.

    Attributes:
        fields (models.StorageFile): All fields of the StorageFile model.
    """

    pass
