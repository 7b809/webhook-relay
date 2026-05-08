from flask import Flask, request, jsonify
import requests
from pymongo import MongoClient
from datetime import datetime, timezone

from config import Config

app = Flask(__name__)

Config.validate()

# -----------------------------------------
# MONGODB SETUP
# -----------------------------------------
mongo_client = MongoClient(Config.MONGO_URI)

db = mongo_client[Config.MONGO_DB]

relay_collection = db[Config.MONGO_COLLECTION]


@app.route("/", methods=["GET"])
def home():
    return {
        "status": "running",
        "service": "webhook-relay"
    }


# -----------------------------------------
# WEBHOOK RELAY
# -----------------------------------------
@app.route("/webhook/<id>", methods=["POST"])
@app.route("/webhook/<id>/", methods=["POST"])
def webhook(id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Invalid payload"
            }), 400

        # -----------------------------------------
        # TARGET URL
        # -----------------------------------------
        target_url = f"{Config.TARGET_BASE_URL}/webhook/{id}/"

        headers = {
            "Content-Type": "application/json",
            "x-api-key": Config.API_KEY
        }

        # -----------------------------------------
        # FORWARD REQUEST
        # -----------------------------------------
        response = requests.post(
            target_url,
            json=data,
            headers=headers,
            timeout=Config.TIMEOUT
        )

        # -----------------------------------------
        # SAVE TO MONGODB
        # -----------------------------------------
        relay_doc = {
            "webhook_id": id,
            "target_url": target_url,
            "payload": data,
            "target_status": response.status_code,
            "target_response": response.text,
            "relay_success": response.ok,
            "created_at": datetime.now(timezone.utc)
        }

        inserted = relay_collection.insert_one(relay_doc)

        return jsonify({
            "status": "forwarded",
            "mongo_id": str(inserted.inserted_id),
            "target_status": response.status_code
        })

    except Exception as e:

        # save failed relay also
        try:
            relay_collection.insert_one({
                "webhook_id": id,
                "payload": request.get_json(silent=True),
                "relay_success": False,
                "error": str(e),
                "created_at": datetime.now(timezone.utc)
            })
        except:
            pass

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)