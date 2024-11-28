from flask import Flask, jsonify, request
from pymongo import MongoClient
from constants import MONGO_URI, MONGO_DBNAME

app = Flask(__name__)

# MongoDB Configuration
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DBNAME]
collection = db["test"]


@app.route("/")
def index():
    try:
        databases = mongo_client.list_database_names()
        message = "Connection Successful!"
        databases = databases
    except Exception as e:
        databases = None
        message = f"Error connecting to MongoDB: {e}"
    return jsonify({"message": message, "databases": databases})


@app.route("/add", methods=["POST"])
def add_document():
    # Insert a document into MongoDB
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    inserted = collection.insert_one(data)
    return jsonify({"message": "Document added", "id": str(inserted.inserted_id)})


@app.route("/list", methods=["GET"])
def list_documents():
    # Fetch all documents from MongoDB
    documents = list(collection.find({}, {"_id": 0}))  # Exclude the _id field for simplicity
    return jsonify(documents)


if __name__ == "__main__":
    app.run(debug=True)
