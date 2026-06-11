import json
import hashlib

with open("data.json") as f:
    raw = json.load(f)

tweets = raw.get("data", [])
users_map = {u["id"]: u for u in raw.get("includes", {}).get("users", [])}

out_users = []
out_posts = []

for tweet in tweets:
    author_id = tweet["author_id"]
    user = users_map.get(author_id, {})

    out_users.append({
        "ext_id": author_id,
        "username": user.get("username", ""),
        "display_name": user.get("name", ""),
        "platform": "x"
    })

    body = tweet["text"]
    post_hash = hashlib.sha256(body.encode()).hexdigest()
    metrics = tweet.get("public_metrics", {})

    out_posts.append({
        "body": body,
        "posts_hash": post_hash,
        "ext_user_id": author_id,
        "likes": metrics.get("like_count", 0),
        "posted_at": tweet.get("created_at")
    })

with open("users.json", "w") as f:
    json.dump(out_users, f)

with open("posts.json", "w") as f:
    json.dump(out_posts, f)