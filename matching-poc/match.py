from datetime import date, timedelta
from email.parser import BytesParser
from email import policy

import numpy as np
from constants import orders_collection, embeddings, s3_client, llm_openai_client
from langchain_core.prompts import PromptTemplate


def download_eml_files_from_s3(s3_bucket_name, s3_file_key, local_download_path):
    """Download all .eml files from the specified S3 bucket and prefix."""
    response = s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix=s3_file_key)
    eml_files = [item["Key"] for item in response.get("Contents", []) if item["Key"].endswith(".eml")]
    local_files = []

    for eml_file in eml_files:
        local_path = f"{local_download_path}/{eml_file.split('/')[-1]}"
        s3_client.download_file(s3_bucket_name, eml_file, local_path)
        local_files.append(local_path)
        print(f"Downloaded: {local_path}")

    return local_files


def parse_eml(file_path):
    with open(file_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
    subject = msg["subject"]
    sender = msg["from"]
    body = msg.get_body(preferencelist=("plain")).get_content()
    return {"subject": subject, "sender": sender, "body": body}


def extract_features(email_content):
    """
    Extract features like supplier details, customer details, product details, etc.
    """
    # Create a Prompt Template for OpenAI
    prompt_template = PromptTemplate(
        input_variables=["email_content"],
        template="""
            Extract the following key details from the email:
            - Supplier details
            - Customer details
            - Product details
            - Purchase Order ID
            - Any references to Order ID or other identifiers.

            Email Content:
            {email_content}
        """,
    )

    # Define a chain to process the document content
    chain = prompt_template | llm_openai_client
    summary = chain.invoke({"email_content": email_content})
    print("DEBUG: summary: ", summary)
    return summary.content


if __name__ == "__main__":
    today = date.today()
    today_str = today.isoformat()
    four_weeks_ago = today - timedelta(weeks=4)
    four_weeks_ago_str = four_weeks_ago.isoformat()

    # Check all the orders created between today and 4 weeks (Assuming Order Lifespan is of 4 weeks)
    orders = list(orders_collection.find({"order_date": {"$gte": four_weeks_ago_str, "$lte": today_str}}, {"_id": 0}))
    # print("DEBUG: Orders: ", orders)

    # Prepare a single line record for each order containing following details from all:
    # - Order ID
    # - Purchase Order
    # - Supplier Details
    # - Customer Details
    # - Product Details
    order_vectors = []
    for order in orders:
        order_text = (
            f"Order ID: {order['order_id']}, Order Date: {order['order_date']}, "
            f"Purchase Order: {order['purchase_order']}, Exp. Order Delivery: {order['expected_delivery_date']}, "
            f"Supplier Name: {order['supplier']['name']}, Supplier Email: {order['supplier']['email']}, "
            f"Supplier Phone: {order['supplier']['phone']}, Supplier Address: {order['supplier']['address']}, "
            f"Buyer Name: {order['buyer']['name']}, Buyer Email: {order['buyer']['email']}, "
            f"Buyer Phone: {order['buyer']['phone']}, Buyer Address: {order['buyer']['address']}, "
            f"Product Details: {order['line_items']}"
        )
        #  Create Embeddings for the Email and Order vectors
        order_vector = embeddings.embed_query(order_text)
        order_vectors.append(order_vector)

    # print("DEBUG: order_vector: ", order_vector)
    # Prepare Email
    s3_bucket_name = "kairav-lighthouz-ai-task"
    s3_file_key = "8ffb7a3e-ec39-494c-8af8-4de449eb12a8/8ffb7a3e-ec39-494c-8af8-4de449eb12a8.eml"
    local_download_path = "/tmp"
    local_files = download_eml_files_from_s3(
        s3_bucket_name=s3_bucket_name, s3_file_key=s3_file_key, local_download_path=local_download_path
    )
    print("DEBUG: local_files: ", local_files)
    email_data = parse_eml(file_path=local_files[0])
    summary_content = extract_features(email_data["body"])
    email_vector = embeddings.embed_query(summary_content)

    similarities = [np.dot(email_vector, ov) for ov in order_vectors]
    best_match_idx = int(np.argmax(similarities))
    best_match_score = similarities[best_match_idx]

    print("DEBUG: High Confidence: ", orders[best_match_idx])
