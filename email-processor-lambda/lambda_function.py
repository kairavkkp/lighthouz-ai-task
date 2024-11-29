import base64
from datetime import datetime
import os
import uuid
import requests
from email.message import EmailMessage
from constants import SCOPES, READ_EMAILS_FROM, SPECIFIC_EMAIL, S3_BUCKET_NAME, API_BASE_URL, msal_client, s3_client


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


def fetch_attachments_from_email(access_token, message_id):
    url = f"https://graph.microsoft.com/v1.0/users/{SPECIFIC_EMAIL}/messages/{message_id}/attachments"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Make the request to fetch messages
    response = requests.get(url, headers=headers)

    # Check for success
    if response.status_code == 200:
        attachments = response.json().get("value", [])
        return attachments
    else:
        print(f"Error fetching attachments: {response.status_code} - {response.text}")
        return []


def mark_email_as_read(access_token, message_id):
    url = f"https://graph.microsoft.com/v1.0/users/{SPECIFIC_EMAIL}/messages/{message_id}"

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"isRead": True}

    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code == 200:
        print(f"Email with ID {message_id} marked as read.")
    else:
        print(f"Failed to mark email as read. Status Code: {response.status_code}")


def create_eml_and_save_to_s3(message_id, access_token, email_data, bucket_name, s3_file_key, email_uuid):
    # Extract necessary fields from the email data
    from_email = email_data["from"]["emailAddress"]["address"]
    to_email = ", ".join([recipient["emailAddress"]["address"] for recipient in email_data["toRecipients"]])
    subject = email_data["subject"]
    body = email_data["body"]["content"]
    sent_date = email_data.get("sentDateTime", datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000"))
    has_attachments = email_data["hasAttachments"]

    # Create an EmailMessage object
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Date"] = sent_date

    # Add the email body
    if email_data["body"]["contentType"] == "html":
        msg.add_alternative(body, subtype="html")
    else:
        msg.set_content(body)

    # Handle attachments
    if has_attachments:
        attachments = fetch_attachments_from_email(access_token, message_id)
        for attachment in attachments:
            filename = attachment["name"]
            content_type = attachment["contentType"]
            attachment_data = base64.b64decode(attachment["contentBytes"])

            # Generate S3 key (path)
            attachment_s3_key = f"{email_uuid}/attachments/{filename}"

            # Upload the attachment to S3
            s3_client.put_object(
                Bucket=bucket_name, Key=attachment_s3_key, Body=attachment_data, ContentType=content_type
            )

        print(f"Attachment {filename} saved to S3 at {attachment_s3_key}")

    # Convert to .eml format
    eml_content = msg.as_bytes()

    # Save to S3
    s3_client.put_object(Bucket=bucket_name, Key=s3_file_key, Body=eml_content, ContentType="message/rfc822")

    print(f"Email saved to S3 at {s3_file_key}")


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

    print("DEBUG: Encountered Emails: ", emails)
    for email_data in emails:
        message_id = email_data.get("id")
        email_uuid = str(uuid.uuid4())
        s3_file_key = os.path.join(email_uuid, f"{email_uuid}.eml")
        _ = create_eml_and_save_to_s3(
            message_id=message_id,
            access_token=access_token,
            email_data=email_data,
            bucket_name=S3_BUCKET_NAME,
            s3_file_key=s3_file_key,
            email_uuid=email_uuid,
        )
        backend_response = requests.post(
            f"{API_BASE_URL}/orders", json={"s3_file_key": s3_file_key, "s3_bucket_name": S3_BUCKET_NAME}
        )
        print("DEBUG: backend_response: ", backend_response)
        mark_email_as_read(access_token=access_token, message_id=message_id)


if __name__ == "__main__":
    lambda_handler(None, None)
