from flask import Flask, request, jsonify
import requests
from pymongo import MongoClient
from datetime import datetime, timezone
import threading

from config import Config

app = Flask(__name__)

Config.validate()

# -----------------------------------------
# MONGODB
# -----------------------------------------
mongo_client = MongoClient(
    Config.MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = mongo_client[Config.MONGO_DB]

relay_collection = db[Config.MONGO_COLLECTION]


# -----------------------------------------
# HOME
# -----------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "service": "webhook-relay"
    })


# -----------------------------------------
# BACKGROUND RELAY FUNCTION
# -----------------------------------------
def process_webhook(webhook_id, data):

    target_url = f"{Config.TARGET_BASE_URL}/webhook/{webhook_id}/"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": Config.API_KEY
    }

    relay_doc = {
        "webhook_id": webhook_id,
        "target_url": target_url,
        "payload": data,
        "relay_success": False,
        "target_status": None,
        "target_response": None,
        "created_at": datetime.now(timezone.utc)
    }

    try:

        # -----------------------------------------
        # FORWARD TO TARGET
        # -----------------------------------------
        response = requests.post(
            target_url,
            json=data,
            headers=headers,
            timeout=Config.TIMEOUT
        )

        relay_doc["relay_success"] = response.ok
        relay_doc["target_status"] = response.status_code
        relay_doc["target_response"] = response.text

    except Exception as e:

        relay_doc["error"] = str(e)

    # -----------------------------------------
    # SAVE FINAL RESULT
    # -----------------------------------------
    try:
        relay_collection.insert_one(relay_doc)
    except Exception as mongo_error:
        print("Mongo save failed:", mongo_error)


# -----------------------------------------
# WEBHOOK ROUTE
# -----------------------------------------
@app.route("/webhook/<id>", methods=["POST"])
@app.route("/webhook/<id>/", methods=["POST"])
def webhook(id):

    try:

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "error": "Invalid payload"
            }), 400

        # -----------------------------------------
        # START BACKGROUND THREAD
        # -----------------------------------------
        threading.Thread(
            target=process_webhook,
            args=(id, data),
            daemon=True
        ).start()

        # -----------------------------------------
        # IMMEDIATE RESPONSE TO TRADINGVIEW
        # -----------------------------------------
        return jsonify({
            "status": "accepted",
            "message": "Webhook received"
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# -----------------------------------------
# IMPORTANT FOR VERCEL
# -----------------------------------------
app = app


if __name__ == "__main__":
    app.run(debug=True)