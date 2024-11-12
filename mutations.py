import os
import re
from datetime import datetime

import pytz
import strawberry
from fastapi.encoders import jsonable_encoder

from db import ccdb, filestoragedb
from mailing import send_mail
from mailing_templates import (
    APPLICANT_CONFIRMATION_BODY,
    APPLICANT_CONFIRMATION_SUBJECT,
    CC_APPLICANT_CONFIRMATION_BODY,
    CC_APPLICANT_CONFIRMATION_SUBJECT,
)
from models import CCRecruitment, StorageFile

# import all models and types
from otypes import (
    CCRecruitmentInput,
    Info,
    MailInput,
    StorageFileInput,
    StorageFileType,
)

inter_communication_secret_global = os.getenv("INTER_COMMUNICATION_SECRET")
ist = pytz.timezone("Asia/Kolkata")


# sample mutation
@strawberry.mutation
def sendMail(
    info: Info,
    mailInput: MailInput,
    inter_communication_secret: str | None = None,
) -> bool:
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
        mail_input["html_body"],
    )

    # send_mail(mail_input["subject"], mail_input["body"],
    # mail_input["to_recipients"], mail_input["cc_recipients"]):

    #     created_sample = Mails.model_validate(
    #         db.mails.find_one({"_id": 0}, {"_id": 0}))
    # else:
    #     # add to database
    #     created_id = db.mails.insert_one(mail_input).inserted_id
    #
    #     # query from database
    #     created_sample = Mails.model_validate(
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

    # Check if the user has already applied
    if ccdb.find_one({"email": cc_recruitment_input["email"]}):
        raise Exception("You have already applied for CC!!")

    # add to database
    created_id = ccdb.insert_one(cc_recruitment_input).inserted_id
    created_sample = CCRecruitment.model_validate(
        ccdb.find_one({"_id": created_id})
    )

    # Send emails
    info.context.background_tasks.add_task(
        send_mail,
        APPLICANT_CONFIRMATION_SUBJECT.safe_substitute(),
        APPLICANT_CONFIRMATION_BODY.safe_substitute(),
        [created_sample.email],
        [],
    )
    info.context.background_tasks.add_task(
        send_mail,
        CC_APPLICANT_CONFIRMATION_SUBJECT.safe_substitute(),
        CC_APPLICANT_CONFIRMATION_BODY.safe_substitute(
            uid=created_sample.uid,
            email=created_sample.email,
            teams=", ".join(created_sample.teams),
            why_this_position=created_sample.why_this_position,
            why_cc=created_sample.why_cc,
            good_fit=created_sample.good_fit,
            ideas=created_sample.ideas,
            other_bodies=created_sample.other_bodies,
            design_experience=created_sample.design_experience or "N/A",
        ),
        ["clubs@iiit.ac.in"],
        [],
    )

    return True


# StorageFile related mutations
@strawberry.mutation
def createStorageFile(
    details: StorageFileInput, info: Info
) -> StorageFileType:
    """
    Create a new storagefile
    returns the created storagefile

    Allowed Roles: ["cc"]
    """
    user = info.context.user

    if user is None or user.get("role") != "cc":
        raise ValueError("You do not have permission to access this resource.")

    # get time info
    current_time = datetime.now(ist)
    time_str = current_time.strftime("%d-%m-%Y %I:%M %p IST")

    storagefile = StorageFile(
        title=details.title,
        url=details.url,
        filetype=details.filetype,
        modified_time=time_str,
        creation_time=time_str,
    )

    # Check if any storagefile with same title already exists
    if filestoragedb.find_one(
        {"title": {"$regex": f"^{re.escape(details.title)}$", "$options": "i"}}
    ):
        raise ValueError("A storagefile already exists with this name.")

    created_id = filestoragedb.insert_one(
        jsonable_encoder(storagefile)
    ).inserted_id
    created_storagefile = filestoragedb.find_one({"_id": created_id})

    return StorageFileType.from_pydantic(
        StorageFile.model_validate(created_storagefile)
    )


@strawberry.mutation
def editStorageFile(
    id: str, details: StorageFileInput, info: Info
) -> StorageFileType:
    """
    Edit an existing storagefile
    returns the edited storagefile

    Allowed Roles: ["cc"]
    """
    user = info.context.user

    if user is None or user.get("role") != "cc":
        raise ValueError("You do not have permission to access this resource.")

    # get time info
    current_time = datetime.now(ist)
    time_str = current_time.strftime("%d-%m-%Y %I:%M %p IST")

    storagefile = filestoragedb.find_one({"_id": id})
    if storagefile is None:
        raise ValueError("StorageFile not found.")

    edited_storagefile = StorageFile(
        _id=id,
        title=details.title,
        url=details.url,
        filetype=details.filetype,
        modified_time=time_str,
        creation_time=storagefile["creation_time"],
    )

    filestoragedb.find_one_and_update(
        {"_id": id}, {"$set": jsonable_encoder(edited_storagefile)}
    )
    updated_storagefile = filestoragedb.find_one({"_id": id})

    return StorageFileType.from_pydantic(
        StorageFile.model_validate(updated_storagefile)
    )


@strawberry.mutation
def deleteStorageFile(id: str, info: Info) -> bool:
    """
    Delete an existing storagefile
    returns a boolean indicating success

    Allowed Roles: ["cc"]
    """
    user = info.context.user

    if user is None or user.get("role") != "cc":
        raise ValueError("You do not have permission to access this resource.")

    storagefile = filestoragedb.find_one({"_id": id})
    if storagefile is None:
        raise ValueError("StorageFile not found.")

    filestoragedb.delete_one({"_id": id})
    return True


# register all mutations
mutations = [
    sendMail,
    ccApply,
    createStorageFile,
    editStorageFile,
    deleteStorageFile,
]
