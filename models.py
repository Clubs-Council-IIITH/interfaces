"""
Data Models for Interfaces Microservice

This file decides what information should be passed in the email to the user and CC.
It has modeks which store information related to recruitment for CC.

It defines the following models:
    Mails: Represents the email to be sent to the user.
    CCRecruitment: Represents the recruitment information to be sent to the CC.
"""

from datetime import datetime
from enum import StrEnum, auto
from typing import Any, List

import strawberry
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic_core import core_schema
from pytz import timezone


def create_utc_time():
    return datetime.now(timezone("UTC"))


class PyObjectId(ObjectId):
    """
    MongoDB ObjectId handler

    This class contains clasmethods to validate and serialize ObjectIds.
    ObjectIds of documents under the Clubs collection are stored under the 'id' field.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        """
        Defines custom schema for Pydantic validation

        This method is used to define the schema for the Pydantic model.

        Args:
            source_type (Any): The source type.
            handler: The handler.

        Returns:
            dict: The schema for the Pydantic model.
        """

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
        """
        Validates the given ObjectId

        Args:
            v (Any): The value to validate.

        Returns:
            ObjectId: The validated ObjectId.

        Raises:
            ValueError: If the given value is not a valid ObjectId.
        """
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        """
        Generates JSON schema

        This method is used to generate the JSON schema for the Pydantic model.

        Args:
            field_schema (dict): The field schema.
        """
        
        field_schema.update(type="string")


# sample pydantic model
class Mails(BaseModel):
    """
    Model for emails

    This model is used to store the email information to be sent.

    Attributes:
        id (PyObjectId): stores the ObjectId of the document.
        uid (str): stores the uid of the user.
        subject (str): stores the subject of the email.
        body (str): stores the body of the email.
        to_recipients (List[EmailStr]): stores the list of 'to' emails.
        cc_recipients (List[EmailStr]): stores the list of 'cc' emails.
        html_body (bool): Whether the email body is in HTML format.
        sent_time (datetime): stores the time when the email was sent.

    Validation:
        to_recipients: Ensures that there are no duplicate emails in the 'to' list.
        cc_recipients: Ensures that there are no duplicate emails in the 'cc' list.

    Raises:
        ValueError: If there are duplicate emails in the 'to' or 'cc' lists.
    """

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    uid: str | None = None
    subject: str = Field(..., max_length=100)
    body: str = Field(...)
    to_recipients: List[EmailStr] = Field(...)
    cc_recipients: List[EmailStr] = Field([])
    html_body: bool = Field(default=False)

    sent_time: datetime = Field(default_factory=create_utc_time, frozen=True)

    @field_validator("to_recipients")
    @classmethod
    # validates the to_recipients field
    def validate_unique_to(cls, value):
        if len(value) != len(set(value)):
            raise ValueError(
                "Duplicate Emails are not allowed in 'to_recipients'"
            )
        return value

    @field_validator("cc_recipients")
    @classmethod
    # validates the cc_recipients field
    def validate_unique_cc(cls, value):
        if len(value) != len(set(value)):
            raise ValueError(
                "Duplicate Emails are not allowed in 'cc_recipients'"
            )
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

# Enum for storing category of the team for the recruit
@strawberry.enum
class Team(StrEnum):
    Design = auto()
    Finance = auto()
    Logistics = auto()
    Stats = auto()


class CCRecruitment(BaseModel):
    """
    Model for CC Recruitment form

    This model is used to store the CC Recruitment form answer information.

    Attributes:
        id (PyObjectId): stores the ObjectId of the document.
        uid (str): stores the uid of the user.
        email (EmailStr): stores the email of the user.
        teams (List[Team]): stores the list of teams the user is applying for.
        design_experience (str): stores the design experience of the user.
        why_this_position (str): stores the reason of the user for applying for this position.
        why_cc (str): stores the reason for applying for CC.
        ideas (str): stores the ideas of the user.
        other_bodies (str): stores the other bodies the user is applying for.
        good_fit (str): stores the reason theuser gives for him being a good fit for CC.
        sent_time (datetime): stores the time when the form was sent.
    """

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

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )
