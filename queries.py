"""
Query Resolvers
"""

import json
import os
from typing import List

import requests
import strawberry

from db import ccdb, docsstoragedb
from models import CCRecruitment, StorageFile

# import all models and types
from otypes import (
    CCRecruitmentType,
    Info,
    SignedURL,
    SignedURLInput,
    StorageFileType,
)

inter_communication_secret = os.getenv("INTER_COMMUNICATION_SECRET")


# fetch signed url from the files service
@strawberry.field
def signedUploadURL(details: SignedURLInput, info: Info) -> SignedURL:
    """
    Uploads file to the files service by any user.

    Args: (Todo: update this)
        Info: contains the user context information.

    Returns:
        SignedURL: A signed URL for uploading a file to the files service.

    Raises:
        Exception: Not logged in!
        Exception: If the request failed.
    """
    user = info.context.user
    if not user:
        raise Exception("Not logged in!")

    # make request to files api
    response = requests.get(
        "http://files/signed-url",
        params={
            "user": json.dumps(user),
            "static_file": "true" if details.static_file else "false",
            "filename": details.filename,
            "inter_communication_secret": inter_communication_secret,
            "max_sizeMB": details.max_size_mb,
        },
    )

    # error handling
    if response.status_code != 200:
        raise Exception(response.text)

    return SignedURL(url=response.text)


@strawberry.field
def ccApplications(info: Info) -> List[CCRecruitmentType]:
    """
    Returns list of all CC Applications for CC.

    Args:
        Info: contains the user's context information.

    Returns:
        List[CCRecruitmentType]: A list of all CC Applications.

    Raises:
        Exception: Not logged in!
        Exception: Not Authenticated to access this API!!
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
    Finds whether any logged in user has applied for CC.

    Args:
        Info: contains the user's context information.

    Returns:
        bool: True if the user has applied for CC, False otherwise.

    Raises:
        Exception: Not logged in!
        Exception: Not Authenticated to access this API!!
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


# Storagefile queries


@strawberry.field
def storagefiles(filetype: str) -> List[StorageFileType]:
    """
    Get all storage files
    Returns a list of storage files with basic info (id and title)
    """
    storage_files = docsstoragedb.find({"filetype": filetype})
    return [
        StorageFileType.from_pydantic(StorageFile.model_validate(storage_file))
        for storage_file in storage_files
    ]


@strawberry.field
def storagefile(file_id: str) -> StorageFileType:
    """
    Get a single storage file by id
    Returns a single storage file with all info
    """
    storage_file = docsstoragedb.find_one({"_id": file_id})
    return StorageFileType.from_pydantic(
        StorageFile.model_validate(storage_file)
    )


# register all queries
queries = [
    signedUploadURL,
    ccApplications,
    haveAppliedForCC,
    storagefiles,
    storagefile,
]
