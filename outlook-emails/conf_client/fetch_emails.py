import msal
import requests

# Azure AD Config
CLIENT_ID = ""
CLIENT_SECRET = ""
TENANT_ID = ""
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]

# Email Configuration
SPECIFIC_EMAIL = "testaccount@lighthouz.onmicrosoft.com"  # Replace with the specific email to filter

# MSAL Client
app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET,
)

# Acquire Token
token_response = app.acquire_token_for_client(scopes=SCOPES)
print("DEBUG: token_response: ", token_response)
if "access_token" in token_response:
    access_token = token_response["access_token"]
    print("Access token acquired.")

    # Graph API request to fetch emails for a specific email address
    url = f"https://graph.microsoft.com/v1.0/users/{SPECIFIC_EMAIL}/messages"
    headers = {"Authorization": f"Bearer {access_token}"}

    # Filtering emails by subject or other criteria (optional)
    filter_query = "$filter=contains(subject, 'Meeting')"  # Modify as needed
    response = requests.get(f"{url}?{filter_query}", headers=headers)

    if response.status_code == 200:
        emails = response.json().get("value", [])
        print(f"Fetched {len(emails)} emails for {SPECIFIC_EMAIL}:")
        for email in emails:
            print(f"Subject: {email['subject']}, From: {email['from']['emailAddress']['address']}")
    else:
        print("Failed to fetch emails:", response.status_code, response.json())
else:
    print("Failed to acquire token:", token_response.get("error_description"))
