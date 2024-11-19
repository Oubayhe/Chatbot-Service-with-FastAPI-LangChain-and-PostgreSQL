import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
         dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER_NAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("HOST")
    )
