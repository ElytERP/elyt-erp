import os
import sys
import yaml
import logging
import psycopg2
from cryptography.fernet import Fernet

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    filename="logs/connection_handler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

class ConnectionHandler:
    def __init__(self, key_file_path="configs/encryption.key"):
        os.makedirs(os.path.dirname(key_file_path), exist_ok=True)
        self.cipher = self.load_key(key_file_path)

    def load_key(self, key_file_path):
        if os.path.exists(key_file_path):
            with open(key_file_path, "rb") as key_file:
                key = key_file.read()
            logging.info("Encryption key loaded.")
        else:
            logging.error("Encryption key not found. Run gen-config.py first.")
            sys.exit(1)
        return Fernet(key)

    def load_connection_details(self, file_path="configs/connection.yml"):
        if not os.path.exists(file_path):
            logging.error(f"Connection file not found: {file_path}")
            raise FileNotFoundError(f"Connection file not found: {file_path}")

        with open(file_path, "rb") as file:
            encrypted_data = file.read()

        decrypted_data = self.cipher.decrypt(encrypted_data)
        connection_details = yaml.safe_load(decrypted_data.decode())

        if "database" not in connection_details:
            raise KeyError("Missing 'database' section in connection.yml")

        logging.info("Connection details loaded successfully.")
        return connection_details

    def get_db_connection(self):
        details = self.load_connection_details()
        db = details["database"]

        try:
            if db["type"] == "postgresql":
                conn = psycopg2.connect(
                    host=db["host"],
                    port=db["port"],
                    dbname=db["name"],
                    user=db["user"],
                    password=db["password"]
                )
                logging.info("PostgreSQL connection established.")
                return conn
            else:
                raise ValueError(f"Unsupported database type: {db['type']}")
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            raise

        
""" example usage:
from connection_handler.connection_handler import ConnectionHandler

handler = ConnectionHandler()
conn = handler.get_db_connection()

with conn.cursor() as cursor:
    cursor.execute("SELECT version();")
    print(cursor.fetchone())

conn.close()
"""