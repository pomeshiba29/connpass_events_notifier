import re

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