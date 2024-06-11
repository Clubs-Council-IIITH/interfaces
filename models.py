import strawberry
from bson import ObjectId
from enum import StrEnum, auto
from pydantic import ConfigDict, BaseModel, Field, EmailStr, field_validator
from pydantic_core import core_schema
from typing import List, Any

from datetime import datetime
from pytz import timezone


def create_utc_time():
    return datetime.now(timezone("UTC"))


# for handling mongo ObjectIds
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        return core_schema.union_schema(
            [
                # check if it's an instance first before doing any further work
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(cls.validate),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


# sample pydantic model
class Mails(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    uid: str | None = None
    subject: str = Field(..., max_length=100)
    body: str = Field(...)
    to_recipients: List[EmailStr] = Field(...)
    cc_recipients: List[EmailStr] = Field([])

    sent_time: datetime = Field(default_factory=create_utc_time, frozen=True)

    @field_validator("to_recipients")
    @classmethod
    def validate_unique_to(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Duplicate Emails are not allowed in 'to_recipients'")
        return value

    @field_validator("cc_recipients")
    @classmethod
    def validate_unique_cc(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Duplicate Emails are not allowed in 'cc_recipients'")
        return value

    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.  # noqa: E501
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


@strawberry.enum
class Team(StrEnum):
    Design = auto()
    Finance = auto()
    Logistics = auto()
    Stats = auto()


class CCRecruitment(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    uid: str = Field(..., max_length=100)
    email: EmailStr = Field(...)

    teams: List[Team] = []
    design_experience: str | None = None

    why_this_position: str = Field()
    why_cc: str = Field()
    ideas: str = Field()
    other_bodies: str | None = None
    good_fit: str = Field()

    sent_time: datetime = Field(default_factory=create_utc_time, frozen=True)

    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.  # noqa: E501
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )
