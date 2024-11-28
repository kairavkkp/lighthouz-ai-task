import os
import boto3
from langchain_openai import ChatOpenAI

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
OPENAI_KEY = os.getenv("OPENAI_KEY")
s3_client = boto3.client("s3", region_name="ap-south-1")

# OpenAI Configuration
llm_openai_client = ChatOpenAI(openai_api_key=OPENAI_KEY, model_name="gpt-4o-mini")
