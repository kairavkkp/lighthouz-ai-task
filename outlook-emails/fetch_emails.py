import os
import msal
import requests

# Azure AD Application credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = "consumers"
AUTHORITY_URL = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "http://localhost"  # Replace with your app's redirect URI
SCOPES = ["Mail.Read"]  # Requested delegated permissions


def fetch_token(auth_code):
    """Fetch an access token using the authorization code."""
    app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY_URL, client_credential=CLIENT_SECRET)
    token_response = app.acquire_token_by_authorization_code(auth_code, scopes=SCOPES, redirect_uri=REDIRECT_URI)
    if "access_token" in token_response:
        return token_response["access_token"]
    else:
        raise Exception(f"Failed to acquire token: {token_response.get('error_description')}")


def fetch_emails(access_token):
    """Fetch emails from Microsoft Graph API."""
    url = "https://graph.microsoft.com/v1.0/me/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch emails: {response.status_code} - {response.text}")


if __name__ == "__main__":
    try:
        # Get the authorization code from the user
        auth_code = ""
        # Step 1: Fetch Access Token
        token = fetch_token(auth_code)
        print("Access token acquired!")

        # Step 2: Fetch Emails
        emails = fetch_emails(token)
        print("Emails fetched successfully!")
        for email in emails.get("value", []):
            print(f"Subject: {email['subject']}")
            print(f"From: {email['from']['emailAddress']['address']}")
            print(f"Received: {email['receivedDateTime']}")
            print("-" * 40)

    except Exception as e:
        print(f"Error: {e}")
