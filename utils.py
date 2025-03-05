import os
from datetime import datetime

import pytz
import requests

inter_communication_secret = os.getenv("INTER_COMMUNICATION_SECRET")
ist = pytz.timezone("Asia/Kolkata")
utc = pytz.timezone("UTC")


def delete_file(filename) -> str:
    """
    Makes a request to delete a file from the files service

    Args:
        filename (str): The name of the file to delete

    Returns:
        (str): The response from the files service

    Raises:
        Exception: If the response is not successful
    """
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
    """
    Returns current time according to UTC timezone
    """
    return datetime.now(utc)


def get_curr_time_str():
    """
    Returns current IST time in YYYY-MM-DD HH:MM:SS format
    """
    return datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
