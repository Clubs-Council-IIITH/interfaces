import os
from datetime import datetime

import pytz
import requests

inter_communication_secret = os.getenv("INTER_COMMUNICATION_SECRET")
ist = pytz.timezone("Asia/Kolkata")
utc = pytz.timezone("UTC")


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


def get_utc_time():
    return datetime.now(utc)


def get_curr_time_str():
    return datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
