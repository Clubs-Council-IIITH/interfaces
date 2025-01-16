"""
Program to send email via Microsoft Graph API

Attributes:
    TENANT_ID (str): Tenant ID for Microsoft Graph API.
    CLIENT_ID (str): Client ID for Microsoft Graph API.
    CLIENT_SECRET (str): Client Secret for Microsoft Graph API.
    CLIENT_EMAIL (str): Client Email for Microsoft Graph API.
"""

import os

import msal
from office365.graph_client import GraphClient
from office365.outlook.mail.item_body import ItemBody

TENANT_ID = os.environ.get("AD_TENANT_ID")
CLIENT_ID = os.environ.get("AD_CLIENT_ID")
CLIENT_SECRET = os.environ.get("AD_CLIENT_SECRET")
CLIENT_EMAIL = os.environ.get("AD_CLIENT_EMAIL")


def acquire_token():
    """
    Returns token aquired via MSAL
    """

    authority_url = f"https://login.microsoftonline.com/{TENANT_ID}/"
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id=f"{CLIENT_ID}",
        client_credential=f"{CLIENT_SECRET}",
    )
    token = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    return token


def send_mail(
    subject: str,
    body: str,
    to: list,
    cc: list = [],
    html_body: bool | None = False,
):
    """
    Method to send email

    Args:
        subject (str): subject for an email.
        body (str): body of the email.
        to (list): The list of recipients for an email.
        cc (list, optional): The list of recipients for an email. Defaults is empty.
        html_body (bool, optional): Whether the body is HTML or not. Defaults to False.

    Returns:
        bool: Whether the email was sent successfully or not.
    """
    
    client = GraphClient(acquire_token)

    if html_body:
        body = ItemBody(content=body, content_type="HTML")

    client.users[CLIENT_EMAIL].send_mail(
        subject=subject,
        body=body,
        to_recipients=to,
        cc_recipients=cc,
        # save_to_sent_items= "false"
    ).execute_query()

    return True

    # except Exception:
    #     return False
    #
    # return True
