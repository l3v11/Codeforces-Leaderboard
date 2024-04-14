import json

with open('cf_handles.json', 'r') as f:
    config = json.load(f)

CF_HANDLES = config.get("CF_HANDLES", "")
if not CF_HANDLES:
    print("CF_HANDLE variable is missing")
    exit(1)

handles = [handle.strip() for handle in CF_HANDLES.split()]
