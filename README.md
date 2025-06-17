# 🔔 connpass イベント通知Bot（GPT評価付き）

## ⚠️ ご利用にあたっての注意（connpass API 規約）

本プロジェクトは [connpass API 利用規約](https://help.connpass.com/api/api-term) を遵守しています。

- connpass API で取得したイベント情報は **個人利用および通知目的**に限定しています。
- **イベント情報の再配信・改変・商用利用は行っていません。**
- Slack通知にはイベントの **公式URLを明記し、出典元を明示**しています。
- APIキーなどの機密情報は `.env` や GitHub Secrets によって安全に管理されています。

---

## 📌 概要

このリポジトリは、**connpass API で取得した最新イベント情報を OpenAI GPT で要約・スコア付けし、上位3件をSlackに通知する自動化Bot**です。

- GitHub Actions による毎週金曜 9:00（JST）の自動実行
- 検索条件や評価基準は `config/config.json` で柔軟に管理
- Slack Webhook でチームへイベントを即時共有可能

---

## 🧱 システム構成

- GitHub Actions により自動実行
  - `main.py`：全体制御
  - `fetcher.py`：connpass APIでイベント取得
  - `scoring.py`：GPTで要約＋スコア評価
  - `selector.py`：平均スコア抽出＋Top3整形
  - `notifier.py`：Slack通知

## 🚀 GitHub Actions でのセットアップ（推奨）

### ✅ 1. リポジトリを Fork する

このリポジトリ右上の「Fork」ボタンを押して、自分のGitHubアカウントにコピーしてください。

### ✅ 2. Secrets を登録する（Settings > Secrets > Actions）

| Name               | 値（例）                       |
|--------------------|--------------------------------|
| `CONNPASS_API_KEY` | connpass APIキー               |
| `OPENAI_API_KEY`   | OpenAI GPTのAPIキー            |
| `SLACK_WEBHOOK_URL`| Slack Webhook URL（通知用）    |

> ※ APIキーやWebhookは個人で発行してください。共有は非推奨です。

### ✅ 3. GitHub Actions を有効化する

1. `Actions` タブを開く
2. 初回は「Enable Workflow」ボタンが表示されるのでクリック

### ✅ 4. 手動実行 or 自動実行で動作確認

- 手動実行：`Actions` タブ > `Run workflow`
- 自動実行：毎週金曜 午前9時に `cron` により実行されます

---

## ⚙️ 設定ファイル（`config/config.json`）→任意で変更可能(デフォルトは以下)

```json
{
  "search": {
    "keywords": ["生成AI", "LLM", "Claude", "RAG", "Gemini"],
    "count": 10,
    "online_only": true,
    "exclude_titles": ["もくもく会", "MokuMoku会"]
  },
  "scoring": {
    "criteria": [
      "①生成AIの実務的な開発スキルが高められるか",
      "②対象者のレベルが中級以上か",
      "③ハンズオン（実践演習）があるか",
      "④登壇者の信頼性（専門性・実績）"
    ],
    "summary_limit": "【概要】概要を3行以内で要約してください。",
    "score_format": "【平均スコア】平均スコアを以下の形式で明示してください：\n4.25点",
    "model": "gpt-3.5-turbo",
    "temperature": 0.3,
    "max_tokens": 900,
    "system_role": "あなたは生成AIイベントの評価専門家です。"
  }
}
```
## 📦 使用ライブラリ（requirements.txt）

- openai
- httpx
- python-dotenv
- beautifulsoup4
- python-dateutil

## 🔔 通知例（Slack）
```text
🔝 今週の上位3件のイベント紹介：

---
【第1位】生成AI活用セミナー
📅 開催日時：2025-06-21 19:00
📍 オンライン
平均スコア：4.75点
🔗 https://connpass.com/event/00000/
```
## 🧪 ローカルでのテスト実行(参考)

```bash
# 1. .env ファイルを作成(※ローカル上でのみ管理し、公開は禁止)
CONNPASS_API_KEY=your_connpass_api_key
OPENAI_API_KEY=your_openai_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url

# 2. 依存パッケージのインストール
pip install -r requirements.txt

# 3. 実行
python main.py
```

## 📝 参考リンク
- connpass API 利用規約: https://help.connpass.com/api/api-term

- OpenAI API: https://platform.openai.com/

- Slack Webhook 設定: https://api.slack.com/messaging/webhooks