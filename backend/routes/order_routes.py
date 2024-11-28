import threading
from flask import Blueprint, jsonify, request
from settings import orders_collection
from background_tasks.orders import extract_data_for_order

order_bp = Blueprint("order", __name__)


@order_bp.route("/", methods=["GET"])
def get_orders():
    # Fetch all documents from MongoDB
    documents = list(orders_collection.find({}, {"_id": 0}))
    return jsonify(documents)


@order_bp.route("/", methods=["POST"])
def add_order():
    """
    Data:
    {
        "s3_bucket_name": "",
        "s3_file_key": ""
    }
    """

    data = request.json
    # Trigger the background task
    thread = threading.Thread(target=extract_data_for_order, args=(data,))
    thread.start()
    return jsonify({"message": "Request received, task started"}), 202
