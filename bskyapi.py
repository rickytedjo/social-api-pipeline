# bskyapi.py
import json
import hashlib
import sys

with open("data.json") as f:
    raw = json.load(f)

posts_raw = raw.get("feed", raw.get("posts", []))

out_users = []
out_posts = []

for item in posts_raw:
    # Bluesky nests the post under "post" key in feed, or is the item itself
    post = item.get("post", item)
    author = post.get("author", {})
    record = post.get("record", {})

    # Map to users schema
    out_users.append({
        "ext_id": author.get("did", ""),          # DID is the stable unique ID
        "username": author.get("handle", ""),
        "display_name": author.get("displayName", ""),
        "platform": "bluesky"
    })

    # Extract body text
    body = record.get("text", "")
    post_hash = hashlib.sha256(body.encode()).hexdigest()

    out_posts.append({
        "body": body,
        "posts_hash": post_hash,
        "ext_user_id": author.get("did", ""),
        "likes": post.get("likeCount", 0),
        "posted_at": record.get("createdAt", post.get("indexedAt", ""))
    })

with open("users.json", "w") as f:
    json.dump(out_users, f)

with open("posts.json", "w") as f:
    json.dump(out_posts, f)