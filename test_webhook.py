import os

import requests
from dotenv import load_dotenv

load_dotenv()

url = os.environ["N8N_WEBHOOK_URL"]

user_message = "Hi how are you?"
response = requests.post(url, json={"message": user_message})

print(response.status_code)
print(response.text)