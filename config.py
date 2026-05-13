import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME")

    API_KEY = os.getenv("API_KEY")
    TARGET_URL = os.getenv("TARGET_URL")
    TIMEOUT = int(os.getenv("TIMEOUT", 10))

    @staticmethod
    def validate():
        required = [
            "MONGO_URI",
            "DB_NAME",
            "COLLECTION_NAME"
        ]

        missing = [k for k in required if not getattr(Config, k)]

        if missing:
            raise Exception(f"Missing env variables: {missing}")