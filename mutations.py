import strawberry
from fastapi.encoders import jsonable_encoder

from db import ccdb

# import all models and types
from otypes import Info
from otypes import MailInput, CCRecruitmentInput
from models import CCRecruitment

from mailing import send_mail


# sample mutation
@strawberry.mutation
def sendMail(mailInput: MailInput, info: Info) -> bool:
    user = info.context.user
    if not user:
        raise Exception("Not logged in!")

    if user.get("role", None) not in ["cc", "club", "slo", "slc"]:
        raise Exception("Not Authenticated to access this API!!")

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

@strawberry.mutation
def ccApply(ccRecruitmentInput: CCRecruitmentInput, info: Info) -> bool:
    user = info.context.user
    if not user:
        raise Exception("Not logged in!")

    if user.get("role", None) not in ["public"]:
        raise Exception("Not Authenticated to access this API!!")

    cc_recruitment_input = jsonable_encoder(ccRecruitmentInput.to_pydantic())

    cc_recruitment_input["uid"] = cc_recruitment_input["email"].split("@")[0]

    # add to database
    created_id = ccdb.insert_one(cc_recruitment_input).inserted_id
    created_sample = CCRecruitment.parse_obj(ccdb.find_one({"_id": created_id}))

    # Send mail to the candidate
    send_mail(
        "CC Application",
        "Your application has been received. We will get back to you soon.",
        [created_sample.email],
        ["clubs@iiit.ac.in"],
        # [],
    )

    return True



# register all mutations
mutations = [
    sendMail,
    ccApply,
]
