import os
import psycopg2

# Load .env vars (take off for dockerization)
from dotenv import load_dotenv
load_dotenv()

# Connect to database
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
db = os.getenv("POSTGRES_DB")
host = os.getenv("POSTGRES_HOST")

conn = psycopg2.connect(
    dbname=db,
    user=user,
    password=password,
    host=host,
    port=5432
)
cur = conn.cursor()

# Ping the table
cur.execute("SELECT * FROM bronze.snapshots LIMIT 1;")
result = cur.fetchone()
if result:
    print("bronze.snapshots table is accessible!")
else:
    print("bronze.snapshots table is empty or not accessible.")

cur.close()
conn.close()

print(result[:10])