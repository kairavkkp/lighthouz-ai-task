from flask import Flask, jsonify, request
from flask_cors import CORS
from routes.order_routes import order_bp
from routes.order_email_thread_routes import order_email_thread_bp
from settings import mongo_client, test_collection

app = Flask(__name__)
CORS(app)


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

    inserted = test_collection.insert_one(data)
    return jsonify({"message": "Document added", "id": str(inserted.inserted_id)})


@app.route("/list", methods=["GET"])
def list_documents():
    # Fetch all documents from MongoDB
    documents = list(test_collection.find({}, {"_id": 0}))  # Exclude the _id field for simplicity
    return jsonify(documents)


app.register_blueprint(order_bp, url_prefix="/")
app.register_blueprint(order_email_thread_bp, url_prefix="/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
