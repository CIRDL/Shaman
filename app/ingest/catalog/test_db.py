import os
import psycopg2

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB", "shaman"),
    user=os.getenv("POSTGRES_USER", "shaman"),
    password=os.getenv("POSTGRES_PASSWORD", "shaman"),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=5432
)

cur = conn.cursor()

# Insert a minimal dummy record
cur.execute("""
    INSERT INTO bronze.snapshots (
        source_type,
        source_url,
        content_hash,
        payload_html
    ) VALUES (
        %s, %s, %s, %s
    ) RETURNING id;
""", (
    "test_type",
    "http://example.com",
    "dummyhash",
    "<tbody>dummy</tbody>"
))
inserted_id = cur.fetchone()[0]
print("Inserted row ID:", inserted_id)

# Select the inserted record
cur.execute("SELECT * FROM bronze.snapshots WHERE id = %s;", (inserted_id,))
row = cur.fetchone()
print("Selected row:", row)

conn.commit()
cur.close()
conn.close()
