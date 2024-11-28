import msal
import requests

# Azure AD Config
CLIENT_ID = ""
TENANT_ID = ""  # Use "common" for multi-tenant apps
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/Mail.Read"]

# MSAL Client
app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

# Acquire token via device code
flow = app.initiate_device_flow(scopes=SCOPES)
if "message" in flow:
    print(flow["message"])  # Follow the instructions to sign in
else:
    raise ValueError("Could not initiate device flow. Check your config.")

token = app.acquire_token_by_device_flow(flow)

if "access_token" in token:
    # Access Microsoft Graph API
    headers = {"Authorization": f"Bearer {token['access_token']}"}
    response = requests.get("https://graph.microsoft.com/v1.0/me/messages", headers=headers)
    if response.status_code == 200:
        emails = response.json()
        print("Emails fetched successfully:", emails)
    else:
        print("Error fetching emails:", response.json())
else:
    print("Error acquiring token:", token)
