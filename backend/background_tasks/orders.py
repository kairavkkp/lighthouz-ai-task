import json
import os
from email import message_from_file
from email.message import Message
from email.utils import parsedate_to_datetime
from utils.match import match_order_from_email
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import UnstructuredEmailLoader
from settings import s3_client, llm_openai_client, orders_collection, order_email_threads_collection, aws_region
from prompts.order_extraction_prompt import ORDER_DATA_EXTRACTION_PROMPT
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


def download_eml_files_from_s3(s3_bucket_name, s3_file_key, local_download_path):
    response = s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix=s3_file_key)
    eml_files = [item["Key"] for item in response.get("Contents", []) if item["Key"].endswith(".eml")]
    local_files = []

    for eml_file in eml_files:
        local_path = f"{local_download_path}/{eml_file.split('/')[-1]}"
        s3_client.download_file(s3_bucket_name, eml_file, local_path)
        local_files.append(local_path)
        print(f"Downloaded: {local_path}")

    return local_files


def process_attachments(s3_bucket_name, prefix):
    public_uris = []

    response = s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix=prefix)

    # Check if objects are present
    if "Contents" not in response:
        print(f"No files found under prefix: {prefix}")
        return public_uris

    # Generate public URIs for each file
    for obj in response["Contents"]:
        file_key = obj["Key"]
        public_uri = f"https://{s3_bucket_name}.{aws_region}.amazonaws.com/{file_key}"
        public_uris.append(public_uri)

    return public_uris


def extract_email_metadata(eml_file_path):
    """
    Extracts metadata (To, From, Subject, Timestamp) from an EML file.

    :param eml_file_path: Path to the EML file
    :return: A dictionary containing metadata
    """
    try:
        # Read and parse the EML file
        with open(eml_file_path, "r") as eml_file:
            msg = message_from_file(eml_file)

        # Extract metadata
        from_email = msg.get("From")
        to_email = msg.get("To")
        subject = msg.get("Subject")
        timestamp = msg.get("Date")

        # Check for attachments
        has_attachments = any(
            part.get_content_disposition() == "attachment" for part in msg.walk() if isinstance(part, Message)
        )

        # Parse timestamp into a datetime object
        parsed_timestamp = None
        if timestamp:
            try:
                parsed_timestamp = parsedate_to_datetime(timestamp)
            except Exception as e:
                print(f"Error parsing timestamp: {e}")

        return {
            "from_email": from_email,
            "to_email": to_email,
            "subject": subject,
            "timestamp": parsed_timestamp,
            "has_attachments": has_attachments,
        }
    except FileNotFoundError:
        print(f"File not found: {eml_file_path}")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def convert_to_langchain_document(path):
    loader = UnstructuredEmailLoader(path)
    data = loader.load()
    return data


def delete_local_file(file_path):
    """
    Deletes a file from the local filesystem.

    :param file_path: Path to the file to delete
    :return: True if file was deleted, else False
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File successfully deleted: {file_path}")
            return True
        else:
            print(f"File not found: {file_path}")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def insert_order_if_not_exists(order_data):
    """
    Updates or inserts a document in the 'order' collection based on `order_id` and `supplier.name`.

    :param db: The MongoDB database instance
    :param order_data: The JSON data to upsert
    """
    try:
        # Define the filter based on `order_id` and `supplier.name`
        filter_criteria = {"order_id": order_data["order_id"], "supplier.name": order_data["supplier"]["name"]}

        # Use update_one with upsert=True
        result = orders_collection.update_one(
            filter_criteria,
            {"$set": order_data},
            upsert=False,
        )

        if result.matched_count > 0:
            print("Document updated successfully.")
        elif result.upserted_id is not None:
            print(f"Document inserted with ID: {result.upserted_id}")
        else:
            print("No action was performed.")
    except Exception as e:
        print(f"An error occurred: {e}")


def extract_data_for_order(data):
    """
    S3 File key should follow a naming convention such as:
    bucket/
        - <uuid-v4>/
            - <uuid-v4>.eml
    """
    # Fetch Details from the Request Payload
    s3_bucket_name = data.get("s3_bucket_name")
    s3_file_key = data.get("s3_file_key")

    # Based on File key, the path will always be an UUID
    email_file_path, _ = os.path.split(s3_file_key)

    local_download_path = "/tmp"

    # Download .eml files from S3
    eml_file_paths = download_eml_files_from_s3(
        s3_bucket_name=s3_bucket_name, s3_file_key=s3_file_key, local_download_path=local_download_path
    )
    eml_file_path = eml_file_paths[0]

    # Parse Attachments
    attachment_file_list = process_attachments(s3_bucket_name=s3_bucket_name, prefix=email_file_path)

    # Parse Email Metadata
    email_metadata = extract_email_metadata(eml_file_path=eml_file_path)

    if email_metadata.get("has_attachments"):
        # Parse .eml files as Documents
        documents = None
        documents = convert_to_langchain_document(path=eml_file_path)
        print("DEBUG: documents: ", documents)

        # Create a Prompt Template for OpenAI
        prompt_template = PromptTemplate(
            input_variables=["prompt", "document_content"],
            template="""
            {prompt}\n\n{document_content}
            """,
        )

        # Define a chain to process the document content
        doc = documents[0]
        chain = prompt_template | llm_openai_client
        summary = chain.invoke({"document_content": doc.page_content, "prompt": ORDER_DATA_EXTRACTION_PROMPT})

        # Output the results
        print("Source:", doc.metadata["source"])
        print("Summary:", summary)
        order_summary_dict = json.loads(summary.content)

        # Deleting Email Summary as its a part of Email Thread and not Order object.
        try:
            del order_summary_dict["email_summary"]
        except Exception:
            pass

        order_summary_string = json.dumps(order_summary_dict)
        order_summary_byte_data = order_summary_string.encode("utf-8")

        # Save the file back to S3 for later operations if required.
        s3_summary_file_key = os.path.join(email_file_path, "summary.json")
        s3_client.put_object(Bucket=s3_bucket_name, Key=s3_summary_file_key, Body=order_summary_byte_data)

        # Upsert Order Object if it exists
        _ = insert_order_if_not_exists(order_data=order_summary_dict)

    best_matched_order = match_order_from_email(eml_file_path)
    print("DEBUG: best_matched_order: ", best_matched_order)
    best_matched_order_id = best_matched_order.get("order").get("order_id")
    email_summary = best_matched_order.get("email_summary")

    # Add Communication for the Email Thread in the collection.
    email_metadata.update(
        {
            "order_id": best_matched_order_id,
            "attachments": attachment_file_list,
            "email_summary": email_summary,
        }
    )
    _ = order_email_threads_collection.insert_one(email_metadata)

    # Delete the files locally to avoid storage/memory leaks
    for eml_file_path in eml_file_paths:
        delete_local_file(file_path=eml_file_path)
    return
