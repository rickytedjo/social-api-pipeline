# build_manifest.py
import json

with open("topics.json") as f:
    topics = json.load(f)

with open("outputs_x.json") as f:
    x_script = json.load(f)

manifest = {
    "users": [
        x_script[t]["outputFiles"]["users.json"]
        for t in topics if t in x_script
    ],
    "posts": [
        x_script[t]["outputFiles"]["posts.json"]
        for t in topics if t in x_script
    ]
}

print(json.dumps(manifest, indent=2))

with open("manifest.json", "w") as f:
    json.dump(manifest, f)