import strawberry
from fastapi.encoders import jsonable_encoder
import os

# import all models and types
from otypes import Info
from otypes import MailInput

from mailing import send_mail

inter_communication_secret_global = os.getenv("INTER_COMMUNICATION_SECRET")

# sample mutation
@strawberry.mutation
def sendMail(info: Info, mailInput: MailInput, inter_communication_secret: str|None = None) -> bool:
    user = info.context.user
    if not user:
        raise Exception("Not logged in!")

    if user.get("role", None) not in ["cc", "club", "slo", "slc"]:
        raise Exception("Not Authenticated to access this API!!")
    
    if inter_communication_secret != inter_communication_secret_global:
        raise Exception("Authentication Error! Invalid secret!")

    mail_input = jsonable_encoder(mailInput.to_pydantic())

    if mail_input["uid"] is None:
        mail_input["uid"] = user["uid"]

    # send mail as background task
    info.context.background_tasks.add_task(
        send_mail,
        mail_input["subject"],
        mail_input["body"],
        mail_input["to_recipients"],
        mail_input["cc_recipients"],
    )

    # send_mail(mail_input["subject"], mail_input["body"], mail_input["to_recipients"], mail_input["cc_recipients"]):

    #     created_sample = Mails.parse_obj(
    #         db.mails.find_one({"_id": 0}, {"_id": 0}))
    # else:
    #     # add to database
    #     created_id = db.mails.insert_one(mail_input).inserted_id
    #
    #     # query from database
    #     created_sample = Mails.parse_obj(
    #         db.mails.find_one({"_id": created_id}, {"_id": 0}))
    #
    # return MailReturnType.from_pydantic(created_sample)

    return True


# register all mutations
mutations = [
    sendMail,
]
