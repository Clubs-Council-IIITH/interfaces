"""
Query Resolvers

This file contains the query resolvers for GraphQL.

Resolvers:
    signedUploadURL: Returns a signed URL for uploading a file to the files service.
    ccApplications: Returns a list of all CC Applications.
    haveAppliedForCC: Returns a boolean indicating whether the user has applied for CC.
"""

import json
import os
from typing import List

import requests
import strawberry

from db import ccdb
from models import CCRecruitment

# import all models and types
from otypes import CCRecruitmentType, Info, SignedURL

inter_communication_secret = os.getenv("INTER_COMMUNICATION_SECRET")


# fetch signed url from the files service
@strawberry.field
def signedUploadURL(info: Info) -> SignedURL:
    """
    Used for uploading file to the files service.

    Inputs:
        Info: contains the user information.

    Returns:
        SignedURL: A signed URL for uploading a file to the files service.

    Accessibility:
        Public(User need to login)

    Raises Exception:
        Not logged in: If the user is not logged in.
        Exception: If the request to the files service fails.
    """

    user = info.context.user
    if not user:
        raise Exception("Not logged in!")

    # make request to files api
    response = requests.get(
        "http://files/signed-url",
        params={
            "user": json.dumps(user),
            "inter_communication_secret": inter_communication_secret,
        },
    )

    # error handling
    if response.status_code != 200:
        raise Exception(response.text)

    return SignedURL(url=response.text)


@strawberry.field
def ccApplications(info: Info) -> List[CCRecruitmentType]:
    """
    Returns list of all CC Applications.

    Inputs:
        Info: contains the user information.

    Returns:
        List[CCRecruitmentType]: A list of all CC Applications.

    Accessibility:
        Only CC can access.

    Raises Exception:
        Not logged in: If the user is not logged in.
        Not Authenticated to access this API!!: If the user is not authenticated to access.
    """

    user = info.context.user
    if not user:
        raise Exception("Not logged in!")

    if user.get("role", None) not in ["cc"]:
        raise Exception("Not Authenticated to access this API!!")

    results = ccdb.find()
    applications = [
        CCRecruitmentType.from_pydantic(CCRecruitment.model_validate(result))
        for result in results
    ]

    return applications


@strawberry.field
def haveAppliedForCC(info: Info) -> bool:
    """
    Finds whether the logged in user has applied for CC.

    Inputs:
        Info: contains the user information.

    Returns:
        bool: True if the user has applied for CC, False otherwise.

    Accessibility:
        Only Public has full access.

    Raises Exception:
        Not logged in: If the user is not logged in.
        Not Authenticated to access this API!!: If the user is not authenticated to access.
    """

    user = info.context.user
    if not user:
        raise Exception("Not logged in!")

    if user.get("role", None) not in ["public"]:
        raise Exception("Not Authenticated to access this API!!")

    result = ccdb.find_one({"uid": user["uid"]})
    if result:
        return True
    return False


# register all queries
queries = [
    signedUploadURL,
    ccApplications,
    haveAppliedForCC,
]
