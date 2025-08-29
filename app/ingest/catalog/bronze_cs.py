import requests
from bs4 import BeautifulSoup
import os


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
source_type = soup.select_one('li#programrequirementstexttab').get_text(strip=True)
source_url = url
program_code = soup.select_one('h1.page-title').get_text(strip=True)
subject_norm = "CS" # Change to dict key
subject_raw = "C S "
catalog_year = soup.select_one('button#sidebar-toggle span').get_text(strip=True)

# group_name, payload_html, rows_json need to be synced

program_container = soup.select_one('div#programrequirementstextcontainer')

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
host = os.getenv("POSTGRES_HOST", "localhost")

conn_str = f"postgresql://{user}:{password}@{host}:5432/{db}"

# # Iterate through each group, insert connection for each iteration

# group_name = course_group[0][0].get_text(strip=True)
# payload_html = course_group[0][1][0]
# rows_json = payload_html.prettify() #maybe? a little more pre-processing?

# # content_hash   TEXT        NOT NULL,   -- hash of payload_html
# # notes          TEXT
# # selector_used  TEXT,                   -- CSS/XPath you used
