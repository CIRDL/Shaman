import os
import psycopg2
import pandas as pd
from bs4 import BeautifulSoup
import re

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

# Read from bronze table
cur.execute("SELECT * FROM bronze.snapshots;")
results = cur.fetchall()
if results:
    print("bronze.snapshots table is accessible!")
else:
    print("bronze.snapshots table is empty or not accessible.")

columns = [desc[0] for desc in cur.description]
bronze_df = pd.DataFrame(results, columns=columns)

soup = BeautifulSoup(bronze_df.payload_html.loc[0], "html.parser")

courses = soup.find("table", class_="sc_courselist")

rows = courses.find_all("tr")

# Desired classes
desired_classes = [["even"], ["odd"], ["orclass","odd"], ["orclass", "even"]]

# Iterate through rows and extract data
for tr in rows:
    if tr.get("class") in desired_classes:
        print(tr)
        # Either codecol or codecol orclass
        code = tr.find("td", class_="codecol").get_text(strip=True).replace('\xa0', ' ')

        title = tr.find_all("td")[1].get_text(strip=True)
        hours = tr.find("td", class_="hourscol").get_text(strip=True)
        course_tuple = (code, title, hours)
        print(course_tuple, "\n")

cur.close()
conn.close()