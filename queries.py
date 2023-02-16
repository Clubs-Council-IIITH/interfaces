import json
import requests
import strawberry

# import all models and types
from otypes import Info, SignedURL


# fetch signed url from the files service
@strawberry.field
def signedURL(info: Info) -> SignedURL:
    user = info.context.user

    # make request to files api
    response = requests.get(
        "http://files/signed-url", params={"user": json.dumps(user)}
    )

    # error handling
    if response.status_code != 200:
        raise Exception(response.text)

    return SignedURL(url=response.text)


# register all queries
queries = [
    getSignedURL,
]
