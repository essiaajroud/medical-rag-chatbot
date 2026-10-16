import json

def load_data(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)