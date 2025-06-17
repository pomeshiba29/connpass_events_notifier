# --- メイン処理 ---
import json
from fetcher import fetch_online_events
from scoring import score_event_with_gpt
from selector import extract_average_score, format_top_events
from notifier import send_to_slack

# --- config読み込み（必要な場合に再利用） ---
def load_config(path="config/config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

def main():
    print("🚀 イベント取得開始")
    events = fetch_online_events()

    if not events:
        print("⚠️ イベントが見つかりませんでした。Slack通知は行いません。")
        return

    results = []
    for event in events:
        summary = score_event_with_gpt(event)
        score = extract_average_score(summary)
        print(f"🎯 {event['title']} -> score={score}")
        results.append((score, summary, event))

    top3 = sorted(results, key=lambda x: x[0], reverse=True)
    if not top3 or all(score == 0.0 for score, _, _ in top3):
        print("⚠️ スコア付きイベントがありませんでした。Slack通知は行いません。")
        return

    formatted_text = format_top_events(top3)
    send_to_slack(formatted_text)

if __name__ == "__main__":
    main()
