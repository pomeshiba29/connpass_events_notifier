import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time

# .envからAPIキーを読み込む
load_dotenv()

SEARCH_KEYWORDS = ["生成AI", "LLM", "MCP", "RAG"]
SEARCH_AREA = "Tokyo"
COUNT = 5

#descriptionのHTMLタグをカットする関数
def strip_html_tags(html):
    return BeautifulSoup(html or "", "html.parser").get_text()

#connpassAPIでデータを取得する（キーワード：生成AI・LLM・MCP・RAG、地域：東京、上限：5個）
def fetch_compass_events_v2(keyword=SEARCH_KEYWORDS, area=SEARCH_AREA, count=COUNT):
    all_events = []

    base_url = "https://connpass.com/api/v2/events/"
    now = datetime.now().isoformat()
    week_later = (datetime.now() + timedelta(days=7)).isoformat()

    params = {
        "keyword": keyword,
        "area": area,
        "count": count,
        "startedAfter": now,
        "startedBefore": week_later,
        "order": "new"
    }

    headers = {
        "X-API-Key": os.getenv("COMPASS_API_KEY")
    }

    response = httpx.get(base_url, params=params, headers=headers)
        
    events= response.json().get("events", [])
    for event in events:
        all_events.append({
        "title": event.get("title"),
        "started_at": event.get("started_at"),
        "place": event.get("place") or "オンライン",
        "address": event.get("address", ""),
        "accepted": event.get("accepted", 0),
        "limit": event.get("limit", 0),
        "event_id": event.get("id"),
        "description": strip_html_tags(event.get("description", ""))
    })

    time.sleep(1)  # API過負荷防止（1秒インターバル）

    return all_events

#出力確認
# if __name__ == "__main__":
#     events = fetch_compass_events_v2()
#     for e in events[:5]:
#         print(f"{e['title']} ({e['started_at']})")
#         print(f"参加状況：{e['accepted']}/{e['limit']}")
#         print(f"場所：{e['place']}")
#         print(f"URL：https://connpass.com/event/{e['event_id']}/")
#         print(f"説明：{e['description']}...\n")