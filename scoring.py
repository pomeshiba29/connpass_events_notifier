# scoring.py

import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from fetcher import fetch_compass_events_v2
import requests

# --- 初期設定 ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# --- GPTによる要約＋スコアリング ---
def score_event_with_gpt(event):
    prompt = (
        "以下のイベント情報について、要約と評価を行ってください。\n\n"
        "【概要】概要を3行以内で要約してください。\n"
        "【評価項目】以下4項目を1〜5点でスコア評価し、理由を添えてください：\n"
        "① 生成AIの実務的な開発スキルが高められるか\n"
        "② 対象者のレベルが中級以上か\n"
        "③ ハンズオン（実践演習）があるか\n"
        "④ 登壇者の信頼性（専門性・実績）\n"
        "【おすすめ度（5点中）】平均スコアを以下の形式で明示してください：\n"
        "4.25点（5点満点中）\n\n"
        f"▼ イベントタイトル：{event['title']}\n"
        f"▼ 説明文：{event['description']}\n"
        f"▼ 開催日：{event['started_at']}\n"
        f"▼ 場所：{event['place']}\n"
        f"▼ 参加状況：{event['accepted']}人 / {event['limit']}人"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは生成AIイベントの評価専門家です。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=900
    )

    return response.choices[0].message.content

# --- 平均スコアを抽出 ---
def extract_average_score(text):
    match = re.search(r"平均スコア[:：] ?([0-9.]+)", text)
    return float(match.group(1)) if match else 0.0

#アナウンスする日付

# --- 上位3イベントをテキスト整形 ---
def format_top_events(scored_events):
    output = "\n🔝 今週の上位3件のイベント紹介：\n"
    for idx, (score, summary, event) in enumerate(scored_events[:3], start=1):
        url = f"https://connpass.com/event/{event['event_id']}/"
        output += f"\n---\n【第{idx}位】{event['title']}\n"
        output += f"📅 開催日時：{event['started_at']}\n"
        output += f"📍 開催場所：{event['place']}\n"
        output += f"👥 参加状況：{event['accepted']}/{event['limit']}人\n"
        output += f"🔗 URL：{url}\n"
        output += f"📝 GPT評価：\n{summary}\n"
    return output

# --- Slack送信 ---
def send_to_slack(message: str):
    if not SLACK_WEBHOOK_URL:
        raise ValueError("Slack Webhook URLが設定されていません。")
    response = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
    if response.status_code != 200:
        raise Exception(f"Slack送信失敗: {response.status_code} - {response.text}")
    print("✅ Slackへ送信完了")

# --- メイン処理 ---
if __name__ == "__main__":
    print("📥 イベント取得中...")
    events = fetch_compass_events_v2()

    print("🧠 GPTでスコアリング中...")
    results = []
    for event in events:
        summary = score_event_with_gpt(event)
        score = extract_average_score(summary)
        results.append((score, summary, event))

    print("🏆 スコア順で上位3件を抽出中...")
    top3 = sorted(results, key=lambda x: x[0], reverse=True)

    print("📄 Slack用フォーマットを作成中...")
    formatted_text = format_top_events(top3)
    print(formatted_text)

    print("📤 Slackに送信中...")
    send_to_slack(formatted_text)
