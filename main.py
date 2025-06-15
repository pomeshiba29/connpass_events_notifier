# --- メイン処理 ---
from fetcher import fetch_compass_events_v2
from scoring import score_event_with_gpt
from selector import extract_average_score
from selector import format_top_events
from notifier import send_to_slack

def main():
    events = fetch_compass_events_v2()
    results = []
    for event in events:
        summary = score_event_with_gpt(event)
        score = extract_average_score(summary)
        results.append((score, summary, event))

    top3 = sorted(results, key=lambda x: x[0], reverse=True)
    formatted_text = format_top_events(top3)
    send_to_slack(formatted_text)

if __name__ == "__main__":
    main()