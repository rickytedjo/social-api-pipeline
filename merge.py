import json
import glob

all_users = []
all_posts = []

for filepath in sorted(glob.glob("users_*.json")):
    try:
        with open(filepath) as f:
            content = f.read().strip()
            if content:
                all_users.extend(json.loads(content))
    except Exception as e:
        print(f"Skipping {filepath}: {e}")

for filepath in sorted(glob.glob("posts_*.json")):
    try:
        with open(filepath) as f:
            content = f.read().strip()
            if content:
                all_posts.extend(json.loads(content))
    except Exception as e:
        print(f"Skipping {filepath}: {e}")

with open("merged_users.json", "w") as f:
    json.dump(all_users, f)

with open("merged_posts.json", "w") as f:
    json.dump(all_posts, f)

print(f"Merged {len(all_users)} users, {len(all_posts)} posts")