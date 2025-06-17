# --- GPTによるイベント評価 ---
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# --- .envからAPIキー読み込み ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY が設定されていません。")

client = OpenAI(api_key=OPENAI_API_KEY)

# --- config読み込み ---
def load_config(path="config/config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()
scoring_config = config.get("scoring", {})

# 設定値の読み出し
criteria_list = scoring_config.get("criteria", [])
summary_limit = scoring_config.get("summary_limit", "概要を3行以内で要約してください。")
score_format = scoring_config.get("score_format", "【平均スコア】平均スコアを以下の形式で明示してください：\n4.25点")
model = scoring_config.get("model", "gpt-3.5-turbo")
temperature = scoring_config.get("temperature", 0.3)
max_tokens = scoring_config.get("max_tokens", 900)
system_role = scoring_config.get("system_role", "あなたは生成AIイベントの評価専門家です。")

# --- GPTによる要約＋スコアリング ---
def score_event_with_gpt(event):
    criteria_text = "\n".join([f"{i+1} {c}" for i, c in enumerate(criteria_list)])
    prompt = (
        "以下のイベント情報について、要約と評価を行ってください。\n\n"
        f"【概要】{summary_limit}\n"
        f"【評価項目】以下{len(criteria_list)}項目を1〜5点でスコア評価し、理由を添えてください：\n"
        f"{criteria_text}\n"
        f"{score_format}\n\n"
        f"▼ イベントタイトル：{event['title']}\n"
        f"▼ 説明文：{event['description']}\n"
        f"▼ 開催日：{event['started_at']}\n"
        f"▼ 場所：{event['place']}\n"
        f"▼ 参加状況：{event['accepted']}人 / {event['limit']}人"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content
