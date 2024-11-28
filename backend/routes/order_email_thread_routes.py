from flask import Blueprint, jsonify
from settings import order_email_threads_collection
from pymongo import ASCENDING, DESCENDING

order_email_thread_bp = Blueprint("order-email-threads", __name__)


@order_email_thread_bp.route("/<order_id>", methods=["GET"])
def get_order_email_threads(order_id):
    documents = list(order_email_threads_collection.find({"order_id": order_id}, {"_id": 0}).sort({"timestamp": 1}))
    return jsonify(documents)
