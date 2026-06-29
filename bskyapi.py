import json
import time
import urllib.request
import urllib.parse
import urllib.error
import hashlib

with open("config.json") as f:
    config = json.load(f)

BEARER_TOKEN = config["bearer_token"]
TOPICS = config["topics"]
MAX_RESULTS = config.get("max_results", 20)

MAX_RETRIES = 3
RETRY_DELAYS = [5, 15, 60]  # exponential backoff in seconds

def fetch_topic(topic, retries=MAX_RETRIES):
    query = urllib.parse.quote(topic)
    url = (
        f"https://api.x.com/2/tweets/search/recent"
        f"?query={query}"
        f"&max_results={MAX_RESULTS}"
        f"&tweet.fields=public_metrics%2Ccreated_at"
        f"&expansions=author_id"
    )

    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {BEARER_TOKEN}",
    })

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())

        except urllib.error.HTTPError as e:
            # 429 = rate limit, 403 = out of credits
            if e.code == 429:
                delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
                print(f"[{topic}] Rate limited, retrying in {delay}s...")
                time.sleep(delay)
            elif e.code == 403:
                print(f"[{topic}] Out of credits or unauthorized, skipping")
                return None
            elif e.code in [500, 502, 503]:
                delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
                print(f"[{topic}] Server error {e.code}, retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"[{topic}] HTTP error {e.code}, skipping")
                return None

        except Exception as e:
            delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
            print(f"[{topic}] Error: {e}, retrying in {delay}s...")
            time.sleep(delay)

    print(f"[{topic}] All retries exhausted, skipping")
    return None

out_users = []
out_posts = []

for topic in TOPICS:
    print(f"Fetching topic: {topic}")
    raw = fetch_topic(topic)

    if not raw or "data" not in raw:
        print(f"[{topic}] No data returned, skipping")
        continue

    users_map = {
        u["id"]: u
        for u in raw.get("includes", {}).get("users", [])
    }

    for tweet in raw.get("data", []):
        author_id = tweet.get("author_id", "")
        user = users_map.get(author_id, {})

        out_users.append({
            "ext_id": author_id,
            "username": user.get("username", ""),
            "display_name": user.get("name", ""),
            "platform": "x"
        })

        body = tweet.get("text", "")
        metrics = tweet.get("public_metrics", {})

        out_posts.append({
            "body": body,
            "posts_hash": hashlib.sha256(body.encode()).hexdigest(),
            "ext_user_id": author_id,
            "likes": metrics.get("like_count", 0),
            "posted_at": tweet.get("created_at", ""),
            "topic": topic
        })

    print(f"[{topic}] Fetched {len(raw.get('data', []))} tweets")
    time.sleep(1)  # gentle delay between topics

with open("users.json", "w") as f:
    json.dump(out_users, f)

with open("posts.json", "w") as f:
    json.dump(out_posts, f)

print(f"Total: {len(out_users)} users, {len(out_posts)} posts")