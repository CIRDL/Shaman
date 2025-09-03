import requests
from bs4 import BeautifulSoup
import os
import psycopg2
import hashlib


print("Starting degree requirements ingestion...")

# Degree Requirements link
url = 'https://ou-public.courseleaf.com/gallogly-engineering/computer-science/computer-science-bachelor-science/#degreerequirementstext'

# Extract text
try:
    response = requests.get(url)
    response.raise_for_status()
except Exception as e:
    print(f"Error fetching URL {url}: {e}")
    raise

# Create soup object
soup = BeautifulSoup(response.text, 'html.parser')

# Construct record
source_type = soup.select_one('li#degreerequirementstexttab').get_text(strip=True) # e.g. Degree Requirements
source_url = url
program_code = soup.select_one('h1.page-title').get_text(strip=True) # e.g. Computer Science, B.S.
subject_norm = "CS" # Change to dict key
subject_raw = "C S "
catalog_year = soup.select_one('button#sidebar-toggle span').get_text(strip=True) # 2025-2026 Edition

# Grab course list table
group_name = 'General Education'
payload_html = str(soup.select_one('table.sc_courselist'))
content_hash = hashlib.sha256(payload_html.encode('utf-8')).hexdigest()

# Connection ------

# Connect to database
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
db = os.getenv("POSTGRES_DB")
host = os.getenv("POSTGRES_HOST")

conn_str = f"postgresql://{user}:{password}@{host}:5432/{db}"

# Iterate through each group, insert connection for each iteration

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
        program_code,
        subject_norm,
        subject_raw,
        catalog_year,
        group_name,
        content_hash,
        payload_html
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
""", (source_type, source_url, program_code, subject_norm, subject_raw, catalog_year, 
        group_name, content_hash, payload_html))

inserted_id = cur.fetchone()[0]
print("Inserted row ID:", inserted_id)

conn.commit()
cur.close()
conn.close()