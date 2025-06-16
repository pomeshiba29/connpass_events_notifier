import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from dateutil.parser import isoparse
import time

# .envからAPIキーを読み込む
load_dotenv()

SEARCH_KEYWORDS = ["生成AI","LLM","MCP","Claude","GPT","RAG","Gemini"]
COUNT = 10  # 最終出力件数

# descriptionのHTMLタグをカットする関数
def strip_html_tags(html):
    return BeautifulSoup(html or "", "html.parser").get_text()

# 開催地が「オンライン」のみ許可
def is_online_event(place: str) -> bool:
    return place and any(word in place.lower() for word in [
        "オンライン", "zoom", "google meet", "teams", "youtube", "webinar", "youtube live"
    ])

# タイトルに「もくもく会」が含まれていないことを確認
def is_not_mokumoku(title: str) -> bool:
    lower_title = title.lower()
    return "もくもく会" not in lower_title and "mokumoku会" not in lower_title


# connpass APIからオンライン開催の未来イベントを取得
def fetch_online_events():
    base_url = "https://connpass.com/api/v2/events/"
    now = datetime.now(timezone(timedelta(hours=9)))
    week_later = (now + timedelta(days=7)).isoformat()
    all_events = {}

    headers = {
        "X-API-Key": os.getenv("COMPASS_API_KEY")
    }

    for keyword in SEARCH_KEYWORDS:
        params = {
            "keyword": keyword,
            "count": COUNT ,
            "startedAfter": now.isoformat(),
            "startedBefore": week_later,
            "order": "new"
        }

        try:
            response = httpx.get(base_url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
        except httpx.ReadTimeout:
            print(f"⏰ タイムアウト：{keyword}")
            continue
        except Exception as e:
            print(f"⚠️ 取得失敗：{keyword} - {e}")
            continue

        events = response.json().get("events", [])

        for event in events:
            event_start = isoparse(event.get("started_at"))
            place = event.get("place") or ""
            title = event.get("title", "")

            if (
                event_start > now
                and is_online_event(place)
                and is_not_mokumoku(title)
            ):
                event_id = event.get("id")
                if event_id not in all_events:
                    all_events[event_id] = {
                        "title": title,
                        "started_at": event.get("started_at"),
                        "place": place,
                        "address": event.get("address", ""),
                        "accepted": event.get("accepted", 0),
                        "limit": event.get("limit", 0),
                        "event_id": event_id,
                        "description": strip_html_tags(event.get("description", ""))
                    }

        time.sleep(1)  # API過負荷防止

    return list(all_events.values())

# 出力確認
if __name__ == "__main__":
    events = fetch_online_events()
    for e in events:
        print(f"{e['title']} ({e['started_at']})")
        print(f"参加状況：{e['accepted']}/{e['limit']}")
        print(f"開催形式：{e['place']}")
        print(f"URL：https://connpass.com/event/{e['event_id']}/")
        print("---")
