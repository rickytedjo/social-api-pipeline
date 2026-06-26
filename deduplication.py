import json
import glob

all_users = []
all_posts = []

for filepath in sorted(glob.glob("users_*.json")):
  try:
    with open(filepath) as f:
            content = f.read().strip()
            if not content:
                print(f"Skipping empty {filepath}")
                continue
            all_users.extend(json.loads(content))

  except Exception as e:
    print(f"Skipping {filepath}: {e}")

for filepath in sorted(glob.glob("posts_*.json")):
  try:
    with open(filepath) as f:
            content = f.read().strip()
            if not content:
                print(f"Skipping empty {filepath}")
                continue
            all_posts.extend(json.loads(content))
            
  except Exception as e:
    print(f"Skipping {filepath}: {e}")

print(f"Loaded {len(all_users)} users, {len(all_posts)} posts before dedup")

seen_users = set()
unique_users = [
    u for u in all_users
    if u["ext_id"] not in seen_users and not seen_users.add(u["ext_id"])
]

seen_posts = set()
unique_posts = [
    p for p in all_posts
    if p["posts_hash"] not in seen_posts and not seen_posts.add(p["posts_hash"])
]

with open("unique_users.json", "w") as f:
    json.dump(unique_users, f)

with open("unique_posts.json", "w") as f:
    json.dump(unique_posts, f)

print(f"Users: {len(all_users)} → {len(unique_users)} unique")
print(f"Posts: {len(all_posts)} → {len(unique_posts)} unique")