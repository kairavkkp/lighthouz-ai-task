import requests
from constants import SCOPES, READ_EMAILS_FROM, SPECIFIC_EMAIL, msal_client


def fetch_unread_emails_from_sender(access_token, sender_email):
    # Microsoft Graph API URL for fetching messages
    url = f"https://graph.microsoft.com/v1.0/users/{SPECIFIC_EMAIL}/messages"

    # Set up headers for the request
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # OData query to filter unread emails from a specific sender, limiting to 2 results
    params = {"$filter": f"from/emailAddress/address eq '{sender_email}' and isRead eq false", "$top": 2}

    # Make the request to fetch messages
    response = requests.get(url, headers=headers, params=params)

    # Check for success
    if response.status_code == 200:
        emails = response.json().get("value", [])
        return emails
    else:
        print(f"Error fetching emails: {response.status_code} - {response.text}")
        return []


def lambda_handler(event, context):
    # Fetch Access Token for the later flow
    token_response = msal_client.acquire_token_for_client(scopes=SCOPES)
    if "access_token" in token_response:
        access_token = token_response["access_token"]
        print("Access token acquired.")
    else:
        return {"statusCode": 400, "body": "Access Token fetch failed."}

    # Fetch unread emails from sender email
    emails = fetch_unread_emails_from_sender(access_token=access_token, sender_email=READ_EMAILS_FROM)

    if len(emails) == 0:
        return {"statusCode": 200, "body": "No Emails received."}

    print(emails)


if __name__ == "__main__":
    lambda_handler(None, None)
