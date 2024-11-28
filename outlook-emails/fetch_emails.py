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
        auth_code = "1.AcYA3wYvcjUnxUGQp5Hw0beh9Ar99D2Pb9hMlfI7aA3JbN_GAFfGAA.AgABBAIAAADW6jl31mB3T7ugrWTT8pFeAwDs_wUA9P9NnlRErjPtrx4eEqY0u4CtsCEOxUb8zHSSZES1B50E3YW7FQCJ93rZ0T2qHJP8C9gJIHsNeoXEyf97XZ-o-uWiudP9lGmVLQ58opAAyBDIEieJMLjkvaajWI7aAOXXxYF5qhv-UoHKKdN4Vx-yc3aDK0XW4MWKY65DFeqkoLisLaV2Ln7x7U6zezwnGvzvut2-71BHWunGHqI9i50vonlUXb77vgBcZkEmWROzGEKWeQ4EpCr5WUF-nRQX5X3dZMn62c1oDP2oPtX8qOLnMDAPXPm6TbfYCxIJRyl0V2jQ9HQW23b1vluVizavT_IeZS4cA_2unYpssFp2UKg9n1rz7FcK6dHbhbC0cOOY4ajP8Jo5_F8KjxQDlEAfdgFbx1BagXoiL4kgLTL61T8oeVP1kz4Hsn0eL6ZCGBZrSXBg76LcMj843_tl7kvtURUrZ4sX0UtTvvdn_ClG4JoFCVX5604grBkc2pQ2YjdQF4uNVxi3s__yNBErg0iSSOTWC7EJDqZm15Vb5dmC66ONmTpuki67A8hvOF0NSEb39vCh5G0Jn3C8L0A0_ym8PMaibSocT9JNSS5Uk8P3WSEbayCM0euz4nvIpiWZSwY2Yh8o7tHaRt6d5eP8rBTm-kNHbYakihI8dXJ8MPCDDqlujo8XQ923j-FKA4zV9NQcbEiRpI0FWi22jwVmzfZg9uFbTppw0fDh_8tz2RqVV-WonHOpRGPikGRLuh3uyg-eGnzEigrFm-Anpt3yAVfMp4ewxivkORigdfa9odutcuGjleueyQcPNxaxK4KfI6O3IKaepX0YUXWUz3ixPJ1NP4j3u1KjfOP5OC0KhNtJAhMCbr6NwqkcxWWlZry6XAx-hI7jfqmHNStPOcxRjElxnx7ISZ9MKMVojMZSmPtdvcg3-70ZVaTiSe-8e6hLgPJ-Gq3HFXH0i_5t6aSJen98hpP35i09Cmxu1S8eU4qHcZQu22nzCBpxPQ7gdiQTp-kxWCjv1tl1OfO-FyeIdObzWH2AhfE6cd3RNE3LHybHKVq_im94AQR3jCJD-Tew5QIGqzI9_cNrpgarS3GLYPA6zvQy-Wpiw7OsIKxQWls0y-HPF_wLEryEpv7Lr0pYIyeo-BP9pziOxgo8mzVOXf8Q9YXnLLFSbaomigK38W6s4ZGWEB-W80GhiNbij05LJvt3BzkQyHo_KN92txm4gWVdMvDHe3A3gmR9DNa1FP79V_D0P7qWnudYzSTsyBNFqJADyLFq2gqiedYf4EJFuQMwPpg6PTtJf1IlkSy6VE3Rwau4RiQKd7VFp-wwpqRKRgYu1edy9RauB8NMSa3q8fWsZXTeW1TD87yZj4UGjNx4bNWSYssk1ZfhpFs"

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
