import os
import boto3
from langchain_openai import ChatOpenAI
from pymongo import MongoClient

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DBNAME]
test_collection = db["test"]
orders_collection = db["orders"]
order_email_threads_collection = db["order-email-threads"]

# S3 Config
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
s3_client = boto3.client("s3", region_name="ap-south-1")

# OpenAI Configuration
OPENAI_KEY = os.getenv("OPENAI_KEY")
llm_openai_client = ChatOpenAI(openai_api_key=OPENAI_KEY, model_name="gpt-4o-mini")
