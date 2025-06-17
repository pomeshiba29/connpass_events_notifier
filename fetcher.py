import httpx
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from dateutil.parser import isoparse
import time

# --- .envの読み込み（ローカル実行時用） ---
load_dotenv()
CONNPASS_API_KEY = os.getenv("CONNPASS_API_KEY")

# --- 設定ファイル（検索条件など）読み込み ---
def load_config(path="config/config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()
search_config = config.get("search", {})

SEARCH_KEYWORDS = search_config.get("keywords", [])
COUNT = search_config.get("count", 10)
EXCLUDE_TITLES = [kw.lower() for kw in search_config.get("exclude_titles", [])]

# --- HTMLタグ除去 ---
def strip_html_tags(html):
    return BeautifulSoup(html or "", "html.parser").get_text()

# --- オンライン開催かどうかの判定 ---
def is_online_event(place: str) -> bool:
    return place and any(word in place.lower() for word in [
        "オンライン", "zoom", "google meet", "teams", "youtube", "webinar", "youtube live"
    ])

# --- タイトルが除外対象でないかの判定 ---
def is_not_excluded(title: str) -> bool:
    lower_title = title.lower()
    return not any(exclude in lower_title for exclude in EXCLUDE_TITLES)

# --- connpass APIからイベント取得 ---
def fetch_online_events():
    if not CONNPASS_API_KEY:
        raise ValueError("❌ CONNPASS_API_KEY が設定されていません。")

    base_url = "https://connpass.com/api/v2/events/"
    now = datetime.now(timezone(timedelta(hours=9)))
    week_later = (now + timedelta(days=7)).isoformat()
    all_events = {}

    headers = {
        "X-API-Key": CONNPASS_API_KEY
    }

    for keyword in SEARCH_KEYWORDS:
        params = {
            "keyword": keyword,
            "count": COUNT,
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
                and (not search_config.get("online_only") or is_online_event(place))
                and is_not_excluded(title)
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

# --- 出力確認 ---
if __name__ == "__main__":
    events = fetch_online_events()
    for e in events:
        print(f"{e['title']} ({e['started_at']})")
        print(f"参加状況：{e['accepted']}/{e['limit']}")
        print(f"開催形式：{e['place']}")
        print(f"URL：https://connpass.com/event/{e['event_id']}/")
        print("---")
