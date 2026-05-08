import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # -----------------------------------------
    # TARGET SERVER
    # -----------------------------------------
    TARGET_BASE_URL = os.getenv("TARGET_BASE_URL"    )

    # -----------------------------------------
    # SECURITY
    # -----------------------------------------
    API_KEY = os.getenv(
        "API_KEY",
        ""
    )

    # -----------------------------------------
    # REQUEST TIMEOUT
    # -----------------------------------------
    TIMEOUT = int(
        os.getenv("TIMEOUT", 10)
    )

    # -----------------------------------------
    # MONGODB
    # -----------------------------------------
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017"
    )

    MONGO_DB = os.getenv(
        "MONGO_DB",
        "webhook_relay"
    )

    MONGO_COLLECTION = os.getenv(
        "MONGO_COLLECTION",
        "relay_logs"
    )

    # -----------------------------------------
    # VALIDATION
    # -----------------------------------------
    @staticmethod
    def validate():

        if not Config.TARGET_BASE_URL:
            raise ValueError(
                "TARGET_BASE_URL is missing in .env"
            )

        if not Config.MONGO_URI:
            raise ValueError(
                "MONGO_URI is missing in .env"
            )