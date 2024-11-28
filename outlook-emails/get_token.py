import msal
import os

# Azure AD Application credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = "consumers"
AUTHORITY_URL = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "http://localhost"  # Replace with your app's redirect URI
SCOPES = ["Mail.Read"]  # Requested delegated permissions


def generate_auth_link():
    """Generate an authentication link for user login."""
    app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY_URL, client_credential=CLIENT_SECRET)
    auth_url = app.get_authorization_request_url(SCOPES, redirect_uri=REDIRECT_URI)
    print("Visit this URL to sign in and copy the authorization code:")
    print(auth_url)


if __name__ == "__main__":
    generate_auth_link()
