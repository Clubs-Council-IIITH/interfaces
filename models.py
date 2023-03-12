from bson import ObjectId
from pydantic import (
    BaseModel,
    Extra,
    Field,
    EmailStr
)

from datetime import datetime

from typing import List

# for handling mongo ObjectIds
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# sample pydantic model
class Mails(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    uid: str | None
    subject: str = Field(..., max_length=100)
    body: str = Field(...)
    to_recipients: List[EmailStr] = Field(..., unique_items=True)
    cc_recipients: List[EmailStr] = Field([], unique_items=True)

    sent_time: datetime = Field(
        default_factory=datetime.utcnow, allow_mutation=False
    )
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = Extra.forbid
        anystr_strip_whitespace = True
        validate_assignment = True
