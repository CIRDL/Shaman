import requests
from bs4 import BeautifulSoup
import os
import psycopg2
import hashlib


print("Starting courses ingestion...")

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
source_type = soup.select_one('li#coursestexttab').get_text(strip=True) # e.g. Does not work :<

print(source_type)