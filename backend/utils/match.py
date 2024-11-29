from email import policy
from datetime import date, timedelta
from email.parser import BytesParser
from langchain_core.prompts import PromptTemplate
import numpy as np
from settings import orders_collection, embeddings, llm_openai_client


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


def match_order_from_email(eml_file_path):
    today = date.today()
    today_str = today.isoformat()
    four_weeks_ago = today - timedelta(weeks=4)
    four_weeks_ago_str = four_weeks_ago.isoformat()

    # Check all the orders created between today and 4 weeks (Assuming Order Lifespan is of 4 weeks)
    orders = list(orders_collection.find({"order_date": {"$gte": four_weeks_ago_str, "$lte": today_str}}, {"_id": 0}))
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

    email_data = parse_eml(file_path=eml_file_path)
    print("DEBUG:email_data: ", email_data)
    summary_content = extract_features(email_data["body"])
    email_vector = embeddings.embed_query(summary_content)

    similarities = [np.dot(email_vector, ov) for ov in order_vectors]
    best_match_idx = int(np.argmax(similarities))
    best_match_score = similarities[best_match_idx]

    return {"order": orders[best_match_idx], "email_summary": summary_content, "confidence": best_match_score}
