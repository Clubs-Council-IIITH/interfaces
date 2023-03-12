import strawberry

from fastapi.encoders import jsonable_encoder

from db import db

# import all models and types
from otypes import Info
from models import Mails
from otypes import MailInput, MailReturnType


# sample mutation
@strawberry.mutation
def sendMail(mailInput: MailInput, info: Info) -> MailReturnType:
    user = info.context.user
    if not user:
        raise Exception("Not logged in!")

    if user.get("role", None) not in ["cc", "club", "slo", "slc"]:
        raise Exception("Not Authenticated to access this API!!")
    
    mail_input = jsonable_encoder(mailInput.to_pydantic())
    
    if mail_input["uid"] is None:
        mail_input["uid"] = user["uid"]

    # add to database
    created_id = db.mails.insert_one(mail_input).inserted_id

    # query from database
    created_sample = Mails.parse_obj(db.mails.find_one({"_id": created_id}, {"_id": 0}))

    return MailReturnType.from_pydantic(created_sample)


# register all mutations
mutations = [
    sendMail,
]
