# 台股 AI 個股分析 - AI 架構調整 v7

本版重點：
- 改成「分析模式 → 執行分析」單一流程，避免 Streamlit 多按鈕 rerun 看起來沒反應。
- 分析模式：
  1. 數據分析｜不呼叫 API
  2. 數據 + AI 詳細分析
  3. 數據 + AI 新聞抓取
  4. 數據 + AI 詳細 + 新聞
- Gemini 詳細分析失敗時，會明確顯示錯誤原因，並保留規則版分析。
- AI 新聞抓取改成「Google News RSS 先抓新聞，Gemini 可用時再整理」，避免 Gemini 搜尋工具失敗時完全沒有內容。
- Gemini 呼叫加入多模型備援：gemini-2.5-flash、gemini-2.0-flash、gemini-1.5-flash。
- Build: 2026-07-03-ai-architecture-v7

上傳方式：覆蓋 GitHub 的 app.py 與 README.md；requirements.txt 不用改。
