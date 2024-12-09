import os

import requests

inter_communication_secret = os.getenv("INTER_COMMUNICATION_SECRET")


def delete_file(filename):
    response = requests.post(
        "http://files/delete-file",
        params={
            "filename": filename,
            "inter_communication_secret": inter_communication_secret,
            "static_file": "true",
        },
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.text
