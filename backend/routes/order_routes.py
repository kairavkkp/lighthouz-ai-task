import threading
from flask import Blueprint, jsonify, request
from settings import orders_collection
from background_tasks.orders import extract_data_for_order

order_bp = Blueprint("order", __name__)


@order_bp.route("/orders", methods=["GET", "OPTIONS"])
def get_orders():
    # Fetch all documents from MongoDB
    documents = list(orders_collection.find({}, {"_id": 0}))
    return jsonify(documents)


@order_bp.route("/orders/<order_id>", methods=["GET", "OPTIONS"])
def get_order(order_id):
    document = list(orders_collection.find({"order_id": order_id}, {"_id": 0}))[0]
    return jsonify(document)


@order_bp.route("/orders", methods=["POST"])
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
