import json
from typing import List

import requests
import strawberry

from db import ccdb, filestoragedb
from models import CCRecruitment, StorageFile

# import all models and types
from otypes import CCRecruitmentType, Info, SignedURL, StorageFileType


# fetch signed url from the files service
@strawberry.field
def signedUploadURL(info: Info) -> SignedURL:
    user = info.context.user
    if not user:
        raise Exception("Not logged in!")

    # make request to files api
    response = requests.get(
        "http://files/signed-url", params={"user": json.dumps(user)}
    )

    # error handling
    if response.status_code != 200:
        raise Exception(response.text)

    return SignedURL(url=response.text)


@strawberry.field
def ccApplications(info: Info) -> List[CCRecruitmentType]:
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

@strawberry.type
class StorageFilesReturn:
    id: str
    title: str

@strawberry.field
def storagefiles() -> List[StorageFilesReturn]:
    """
    Get all storage files
    Returns a list of storage files with basic info (id and title)
    """
    storage_files = filestoragedb.find()
    return [
        StorageFileBasic(
            id=str(storage_file["_id"]), 
            title=storage_file["title"]
        ) 
        for storage_file in storage_files
    ]


@strawberry.field
def storagefile(id: str) -> StorageFileType:
    """
    Get a storagefile by id
    returns a storagefile
    """
    storagefile = filestoragedb.find_one({"_id": id})
    return StorageFileType.from_pydantic(StorageFile.model_validate(storagefile))

# register all queries
queries = [
    signedUploadURL,
    ccApplications,
    haveAppliedForCC,
    storagefiles,
    storagefile
]
