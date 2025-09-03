import requests
from bs4 import BeautifulSoup
import os
import psycopg2
import hashlib


print("Starting courses ingestion...")

# Major specific courses link
url = 'https://ou-public.courseleaf.com/gallogly-engineering/computer-science/#coursestext'

# Extract text
try:
    response = requests.get(url)
    response.raise_for_status()
except Exception as e:
    print(f"Error fetching URL {url}: {e}")
    raise

# Create soup object
soup = BeautifulSoup(response.text, 'html.parser')

# Grab container of courses
container = soup.find(id='coursestextcontainer')

# Construct record
source_type = container.find('h2').get_text(strip=True)
source_url = url
program_code = soup.select_one('h1.page-title').get_text(strip=True) # e.g. Computer Science, B.S.
subject_norm = "CS" # Change to dict key
subject_raw = "C S "
catalog_year = soup.select_one('button#sidebar-toggle span').get_text(strip=True) # 2025-2026 Edition
group_name = "Major Courses"

# Grab courses
payload_html = soup.find("div", class_="sc_sccoursedescs")
rows_json = payload_html.prettify()
payload_html = str(payload_html)
content_hash = hashlib.sha256(payload_html.encode('utf-8')).hexdigest()

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