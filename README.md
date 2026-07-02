# 台股 AI 個股分析恢復版

這是 Streamlit 可直接部署版。功能：輸入股票代號或中文名稱，串接 FinMind 股價 / 法人籌碼 / 月營收資料，計算技術指標，並用 Google Gemini 產出個股分析。

## 檔案

- `app.py`：主程式
- `requirements.txt`：部署套件
- `.streamlit/config.toml`：Streamlit 介面設定
- `.streamlit/secrets.toml.example`：Secrets 格式範本，不要直接當正式 secrets 上傳

## Streamlit Cloud 部署設定

- Repository：你的 GitHub repo
- Branch：`main`
- Main file path：`app.py`
- Python version：`3.12`

## Secrets 設定

到 Streamlit Cloud：`Manage app → Settings → Secrets`，貼上：

```toml
FINMIND_TOKENS = [
  "你的 FinMind token 1",
  "你的 FinMind token 2",
  "你的 FinMind token 3",
  "你的 FinMind token 4"
]

GOOGLE_API_KEYS = [
  "你的 Google Gemini API key 1",
  "你的 Google Gemini API key 2",
  "你的 Google Gemini API key 3"
]

GOOGLE_MODEL = "gemini-2.5-flash"
```

## 重要提醒

- 不要把 API key / FinMind token 寫進 GitHub。
- `app.py` 已支援 Google Gemini API key 池；任一 key 失敗會自動嘗試下一組。
- 沒有設定 Google key 時，網站仍會使用規則版分析，不會整個掛掉。
