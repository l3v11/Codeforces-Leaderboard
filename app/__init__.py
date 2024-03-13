import os
from dotenv import load_dotenv

load_dotenv('config.env', override=True)

CF_HANDLES = os.environ.get('CF_HANDLES', '')
if not CF_HANDLES:
    print("CF_HANDLE env variable is missing")
    exit(1)

handles = [handle.strip() for handle in CF_HANDLES.split()]
