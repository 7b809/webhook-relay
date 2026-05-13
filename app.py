from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import threading
import requests

from config import Config

app = Flask(__name__)

Config.validate()

# MongoDB
client = MongoClient(Config.MONGO_URI)

db = client[Config.DB_NAME]

collection = db[Config.COLLECTION_NAME]


def forward_alert(data):

    try:

        headers = {"Content-Type": "application/json", "x-api-key": Config.API_KEY}

        requests.post(
            Config.TARGET_URL, json=data, headers=headers, timeout=Config.TIMEOUT
        )

    except Exception as e:
        print(f"Forward Error: {e}")


@app.route("/", methods=["GET"])
def home():
    return {"status": "running"}


@app.route("/webhook/<security_id>", methods=["POST"])
@app.route("/webhook/<security_id>/", methods=["POST"])
def webhook(security_id):

    try:

        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid payload"}), 400

        now = datetime.utcnow()

        date_str = now.strftime("%Y-%m-%d")

        log_entry = {"received_at": now, "data": data}

        # Atomic upsert
        collection.update_one(
            {"security_id": security_id, "date": date_str},
            {"$setOnInsert": {"created_at": now}, "$push": {"logs": log_entry}},
            upsert=True,
        )

        # Background forwarding
        threading.Thread(target=forward_alert, args=(data,), daemon=True).start()

        # RETURN FAST
        return jsonify({"status": "received", "security_id": security_id}), 200

    except Exception as e:

        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
