import requests
from bs4 import BeautifulSoup
import os
import psycopg2
import hashlib
from psycopg2.extras import Json


print("Starting classnav ingestion...")

# Program Requirements request

url = "https://classnav.ou.edu/index_ajax.php"
params = {
    "sEcho": 1,
    "iColumns": 18,
    "sColumns": "",
    "iDisplayStart": 0,
    "iDisplayLength": 400,
    "semester": "202420",
    "subject_code": "C S",
    "subject": "C S",
    "schedule": "all",
    "delivery": "all",
    "gened": "",
    "term": "all",
    "available": "true",
    "waitlist": "true"
}

# Hit request link
try:
    response = requests.get(url)
    response.raise_for_status()
except Exception as e:
    print(f"Error fetching URL {url}: {e}")
    raise

# Extract data
resp = requests.get(url, params=params)
data = resp.json()

# Construct record
source_type = 'Classnav'
source_url = url
group_name = "Major Courses"

# Grab courses
payload_html = str(data) # table under aaData
rows_json = data
content_hash = hashlib.sha256(payload_html.encode('utf-8')).hexdigest()
term_id = '202420'

# Connection ------

# Connect to database
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
db = os.getenv("POSTGRES_DB")
host = os.getenv("POSTGRES_HOST")

conn_str = f"postgresql://{user}:{password}@{host}:5432/{db}"

# Create connection to database
conn = psycopg2.connect(
    dbname=db,
    user=user,
    password=password,
    host=host,
    port=5432
)
cur = conn.cursor()

cur.execute("""
    INSERT INTO bronze.snapshots (
        source_type,
        source_url,
        group_name,
        content_hash,
        rows_json,
        term_id,
        payload_html
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
""", (source_type, source_url, group_name, content_hash, Json(rows_json), term_id, payload_html))

inserted_id = cur.fetchone()[0]
print("Inserted row ID:", inserted_id)

conn.commit()
cur.close()
conn.close()