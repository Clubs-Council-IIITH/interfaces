import msal
from office365.graph_client import GraphClient
import os

TENANT_ID = os.environ.get("AD_TENANT_ID")
CLIENT_ID = os.environ.get("AD_CLIENT_ID")
CLIENT_SECRET = os.environ.get("AD_CLIENT_SECRET")
CLIENT_EMAIL = os.environ.get("AD_CLIENT_EMAIL")


def acquire_token():
    """
    Acquire token via MSAL
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


def send_mail(subject, body, to, cc=[]):
    # try:
    client = GraphClient(acquire_token)

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
