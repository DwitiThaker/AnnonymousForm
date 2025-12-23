import json

with open("new-key.json") as f:
    print(json.dumps(json.load(f)))
