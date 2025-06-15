# --- Slack送信 ---
import os
import requests
from dotenv import load_dotenv

load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_to_slack(message: str):
    if not SLACK_WEBHOOK_URL:
        raise ValueError("Slack Webhook URLが設定されていません。")
    response = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
    if response.status_code != 200:
        raise Exception(f"Slack送信失敗: {response.status_code} - {response.text}")
    print("✅ Slackへ送信完了")