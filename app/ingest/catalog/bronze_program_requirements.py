import requests
from bs4 import BeautifulSoup
import os
import psycopg2
import hashlib


print("Starting program requirements ingestion...")

# Program Requirements link
url = 'https://ou-public.courseleaf.com/gallogly-engineering/computer-science/computer-science-bachelor-science/#programrequirementstext'

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
source_type = soup.select_one('li#programrequirementstexttab').get_text(strip=True) # e.g. Program Requirements
source_url = url
program_code = soup.select_one('h1.page-title').get_text(strip=True) # e.g. Computer Science, B.S.
subject_norm = "CS" # Change to dict key
subject_raw = "C S "
catalog_year = soup.select_one('button#sidebar-toggle span').get_text(strip=True) # 2025-2026 Edition

# Grab container for programs
program_container = soup.select_one('div#programrequirementstextcontainer')

# Extract each group by h2
course_group = []
for h2 in program_container.find_all("h2"):
    tables = []
    for sib in h2.next_siblings:
        # stop when we hit the next section header
        if sib.name == "h2":
            break
        # collect tables within this section
        if sib.name == "table" and "sc_courselist" in (sib.get("class") or []):
            tables.append(sib)
    course_group.append((h2, tables))

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

# Iterate through each group, insert connection for each iteration
for group in course_group:
    group_name = group[0].get_text(strip=True) # e.g. Major Requirements
    payload_html = group[1][0] # <table>...</table>
    rows_json = payload_html.prettify()
    payload_html = str(payload_html)
    content_hash = hashlib.sha256(payload_html.encode('utf-8')).hexdigest()

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
