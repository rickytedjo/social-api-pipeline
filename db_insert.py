import json
import psycopg2

conn = psycopg2.connect(
  host="postgres-coordinator",
  port=5432,
  dbname="kestra",
  user="{{ vars.POSTGRES_USERNAME }}",
  password="{{ vars.POSTGRES_PASSWORD }}"
)
cur = conn.cursor()
with open("unique_users.json") as f:
  users = json.load(f)
# Upsert users, return id mapped to ext_id
ext_id_to_db_id = {}
for u in users:
  cur.execute("""
    INSERT INTO users (ext_id, username, display_name, platform)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (ext_id) DO UPDATE
      SET username = EXCLUDED.username,
          display_name = EXCLUDED.display_name
    RETURNING id, ext_id
  """, (u["ext_id"], u["username"], u["display_name"], u["platform"]))
  row = cur.fetchone()
  ext_id_to_db_id[row[1]] = row[0]
with open("unique_posts.json") as f:
  posts = json.load(f)
# Resolve ext_user_id → users.id then insert posts
for p in posts:
  user_id = ext_id_to_db_id.get(p["ext_user_id"])
  if not user_id:
    continue
  cur.execute("""
    INSERT INTO posts (body, posts_hash, user_id, likes, posted_at)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (posts_hash) DO NOTHING
  """, (p["body"], p["posts_hash"], user_id, p["likes"], p["posted_at"]))
conn.commit()
cur.close()
conn.close()
print("Insert complete")