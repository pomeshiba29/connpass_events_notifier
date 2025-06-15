# GPTによるスコアリング
import os
from dotenv import load_dotenv
from openai import OpenAI


# --- 初期設定 ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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






