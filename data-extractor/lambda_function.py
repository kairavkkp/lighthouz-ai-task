import json
from email import policy
from email.parser import BytesParser
from prompt import PROMPT
from constants import s3_client, llm_openai_client, S3_BUCKET_NAME
from langchain_community.document_loaders import UnstructuredEmailLoader
from langchain.schema.runnable import RunnableSequence
from langchain_core.prompts import PromptTemplate


# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain


def download_eml_files_from_s3(prefix, local_download_path):
    """Download all .eml files from the specified S3 bucket and prefix."""
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
    eml_files = [item["Key"] for item in response.get("Contents", []) if item["Key"].endswith(".eml")]
    local_files = []

    for eml_file in eml_files:
        local_path = f"{local_download_path}/{eml_file.split('/')[-1]}"
        s3_client.download_file(S3_BUCKET_NAME, eml_file, local_path)
        local_files.append(local_path)
        print(f"Downloaded: {local_path}")

    return local_files


def convert_to_langchain_document(path):
    loader = UnstructuredEmailLoader(path)
    data = loader.load()
    return data


def parse_eml(file_path):
    """Parse .eml file and extract subject and body."""

    with open(file_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    subject = msg["subject"]
    body = None

    # Extract body from plain text parts
    if msg.is_multipart():
        for part in msg.iter_parts():
            if part.get_content_type() == "text/plain":
                body = part.get_content().strip()
                break
    else:
        body = msg.get_content().strip()

    return subject, body


def lambda_handler(event, context):
    # AWS S3 Configuration
    S3_PREFIX = "f91481ff-692e-476f-935a-40efc22b76bc.eml"
    LOCAL_DOWNLOAD_PATH = "/tmp"

    # Step 1: Download .eml files from S3
    eml_file_paths = download_eml_files_from_s3(prefix=S3_PREFIX, local_download_path=LOCAL_DOWNLOAD_PATH)

    # Step 2: Parse .eml files
    documents = None
    for eml_file_path in eml_file_paths:
        documents = convert_to_langchain_document(path=eml_file_path)
    print("DEBUG: documents: ", documents)
    # Step 3: Create a Prompt Template for OpenAI
    prompt_template = PromptTemplate(
        input_variables=["prompt", "document_content"],
        template="""
        {prompt}\n\n{document_content}
        """,
    )

    # Define a chain to process the document content
    doc = documents[0]
    chain = prompt_template | llm_openai_client
    summary = chain.invoke({"document_content": doc.page_content, "prompt": PROMPT})
    # Output the results
    print("Source:", doc.metadata["source"])
    print("Summary:", summary)
    parsed_summary = json.loads(summary.content)
    with open("summary.json", "w") as f:
        json.dump(parsed_summary, f)


if __name__ == "__main__":
    lambda_handler(None, None)
