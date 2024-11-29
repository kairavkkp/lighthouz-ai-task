import os
import msal
import boto3

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]
SPECIFIC_EMAIL = "testaccount@lighthouz.onmicrosoft.com"

# Temporarily only reading the emails from my personal email account
READ_EMAILS_FROM = "kairavpithadia13@gmail.com"

s3_client = boto3.client("s3", region_name="ap-south-1")
msal_client = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET,
)
