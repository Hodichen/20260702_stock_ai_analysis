from __future__ import annotations

import json
import math
import os
import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any
from urllib.parse import quote_plus
import re
import xml.etree.ElementTree as ET

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import streamlit as st

APP_TITLE = "台股 AI 個股分析"
APP_BUILD = "2026-07-03-ai-architecture-v7"
FINMIND_API_URL = "https://api.finmindtrade.com/api/v4/data"
EMBEDDED_FINMIND_TOKENS = ['eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZnJlZW9uZXllYXJhaSIsImVtYWlsIjoiZnJlZW9uZXllYXJhaUBnbWFpbC5jb20ifQ.QrpcS4DVlqm7bdsL-bDmGdNTtg8HKzm2rrwJUtf7v24', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiaG9kaWRpZmlubWluZCIsImVtYWlsIjoiaG9kaWRpQGdtYWlsLmNvbSJ9._w1f1blFk5cVtxYkQdArSPuP2nMbcj0ecB5WUOCp1d8', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiaG9kaWRpIiwiZW1haWwiOiJnZW1pbmkyMDI1MTA4QGdtYWlsLmNvbSJ9.hvVPA_bI3YdsapZTQ5m4bJsAeR61z1NgcXBZlm2m4lw', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMjAyNWNoZW5jaGVuMjAyNSIsImVtYWlsIjoiMjAyNWNoZW5jaGVuMjAyNUBnbWFpbC5jb20ifQ.IcNKTcRbriGQOcRAH_y13Tif2aYxKjYv5cRtZVkoOHo']
EMBEDDED_GOOGLE_API_KEYS = ['AIzaSyD41KegJf4ZV1ZpNI2sd4Kd1nJT1HBL_LA', 'AIzaSyD0Mxqd9g8RmAMN6oOSAqi9p8UfudRO8bI', 'AIzaSyAU_Y8Og0wI6HtWLwRNRW7TTGYzyhBlRSY']

st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

CSS = """
<style>
:root{
  --bg:#efebe3; --ink:#433c36; --muted:#867c73; --line:#ddd2c2;
  --card:#fbf8f2; --hero:#f6f0e4; --gold:#b89d6a;
  --earth1:#f3ece1; --earth2:#e7ddd2; --earth3:#e2e5dc; --earth4:#e3d6cf; --earth5:#ece5d8;
  --pos:#c94d42; --neg:#4f8a61; --btn:#c55c52; --btn2:#9a8b70; --btn3:#8b9a92;
  --foreign:#7b8fa6; --trust:#b3946d; --dealer:#9a8395; --total:#706b66;
}
html, body, .stApp{background:var(--bg); color:var(--ink);}
.block-container{max-width:1280px; padding-top:1rem; padding-bottom:4rem;}
section[data-testid="stSidebar"]{display:none!important;} div[data-testid="collapsedControl"]{display:none!important;}
h1,h2,h3,h4{color:var(--ink); letter-spacing:.01em;}
.hero{background:linear-gradient(135deg,#f7f1e7 0%,#ede6da 100%); border:1px solid var(--line); border-top:6px solid var(--gold); border-radius:26px; padding:1.4rem 1.5rem; box-shadow:0 10px 26px rgba(60,48,36,.05); margin-bottom:1rem;}
.hero-title{font-size:2.25rem; font-weight:900; display:flex; align-items:center; gap:.65rem;}
.hero-sub{color:var(--muted); margin-top:.4rem; font-size:.96rem;}
.search-card{background:var(--card); border:1px solid var(--line); border-radius:22px; padding:1rem 1.15rem; box-shadow:0 8px 18px rgba(60,48,36,.05); margin-bottom:1rem;}
.section-gap{height:.75rem;}
.summary-box{background:linear-gradient(135deg,#f5eee3 0%,#efe5d8 100%); border:1px solid #d7c6b1; border-radius:22px; padding:1rem 1.15rem; margin:.75rem 0 1rem; box-shadow:0 6px 15px rgba(60,48,36,.04);}
.summary-title{font-size:1.05rem; color:#7a6540; font-weight:900; margin-bottom:.4rem;}
.summary-text{font-size:1.08rem; line-height:1.9; font-weight:700;}
.summary-sub{font-size:.88rem; color:var(--muted); margin-top:.4rem;}
.metric-card{background:var(--card); border:1px solid var(--line); border-radius:20px; padding:1rem 1.1rem; min-height:128px; box-shadow:0 8px 18px rgba(60,48,36,.05); margin-bottom:.75rem;}
.metric-warm{background:var(--earth1);} .metric-cool{background:var(--earth3);} .metric-soft{background:var(--earth4);} .metric-sand{background:var(--earth5);} .metric-stone{background:var(--earth2);}
.metric-label{color:var(--muted); font-size:.92rem; margin-bottom:.45rem;}
.metric-value{font-size:2rem; font-weight:900; line-height:1.15; color:var(--ink);}
.metric-note{font-size:.9rem; margin-top:.34rem; color:var(--muted);} 
.val-pos{color:var(--pos)!important;} .val-neg{color:var(--neg)!important;} .note-pos{color:var(--pos)!important;} .note-neg{color:var(--neg)!important;}
.badge{display:inline-flex; align-items:center; gap:.35rem; border-radius:999px; padding:.42rem .8rem; font-weight:800; margin:.2rem .25rem .2rem 0; border:1px solid var(--line); background:#fffaf5;}
.badge-pos{color:var(--pos); border-color:#e8bdb6; background:#fff7f5;} .badge-neg{color:var(--neg); border-color:#bcd0c1; background:#f6fbf7;} .badge-mid{color:#7b6a49; border-color:#ddd0b8; background:#fffaf0;} .badge-info{color:#6c7f8a; border-color:#cfdadf; background:#f6fafb;}
.section-card{border-radius:22px; padding:1.15rem 1.2rem; border:1px solid var(--line); box-shadow:0 8px 18px rgba(60,48,36,.05); margin-bottom:1rem;}
.section-neutral{background:var(--card);} .section-tech{background:#f4ede2;} .section-chip{background:#edf1ea;} .section-fund{background:#f1ece8;} .section-ai{background:#f7f0e4;} .section-risk{background:#f8efef;}
.section-title{font-size:1.25rem; font-weight:900; color:#6b5a3f; display:flex; align-items:center; gap:.55rem; margin:0 0 .95rem;}
.title-stick{width:6px; height:28px; border-radius:999px; background:var(--gold); display:inline-block;}
.ai-mini-box{background:#fbf8f2; border:1px solid var(--line); border-radius:20px; padding:1rem 1rem; min-height:220px; box-shadow:0 6px 14px rgba(60,48,36,.04); margin-bottom:1rem;}
.ai-mini-title{font-size:1.08rem; font-weight:900; margin-bottom:.65rem; color:#6b5a3f; display:flex; align-items:center; gap:.5rem;}
.warn-box{background:#fbf2f1; border:1px solid #e6c5c0; color:#6b3b3f; border-radius:18px; padding:1rem 1.05rem; line-height:1.8;}
.small-muted{color:var(--muted); font-size:.88rem;}
.top-btn-row .stButton>button{height:52px; border-radius:16px; font-weight:900; border:none;}
.top-btn-row.primary .stButton>button{background:var(--btn); color:#fff;}
.top-btn-row.secondary .stButton>button{background:var(--btn2); color:#fff;}
.top-btn-row.tertiary .stButton>button{background:var(--btn3); color:#fff;}
[data-testid="stTextInput"] label{font-weight:700; color:var(--ink);} 
[data-testid="stTextInput"] input{border-radius:14px!important; background:#f7f5f0!important;}
.plot-wrap{background:var(--card); border:1px solid var(--line); border-radius:22px; padding:.85rem; margin-top:.25rem; margin-bottom:1rem;}
.footer-tip{color:var(--muted); font-size:.86rem; margin-top:.3rem;}
.institution-foreign{color:var(--foreign)!important;} .institution-trust{color:var(--trust)!important;} .institution-dealer{color:var(--dealer)!important;} .institution-total{color:var(--total)!important;}
hr.soft{border:none; border-top:1px solid #e4dbcf; margin:1rem 0;}

.action-grid{display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.75rem; margin-top:.55rem;}
.action-item{background:#fbf8f2; border:1px solid var(--line); border-radius:16px; padding:.85rem .9rem; line-height:1.65;}
.action-item b{color:#6b5a3f;}
.path-item{background:#f4ede2; border:1px solid #decbb6; border-radius:16px; padding:.85rem .9rem; line-height:1.65; margin-bottom:.65rem;}
.path-label{display:inline-block; min-width:48px; color:#7a6540; font-weight:900;}
.status-box{background:#f9f4ea; border:1px solid #d9c7ae; border-radius:14px; padding:.65rem .75rem; margin:.55rem 0 .65rem; color:#6b5a3f; font-weight:700;}
.status-warn{background:#fbf2f1; border-color:#e6c5c0; color:#78484a;}
@media (max-width: 800px){.action-grid{grid-template-columns:1fr;}}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@dataclass
class StockBundle:
    stock_id: str
    stock_name: str
    industry: str
    prices: pd.DataFrame
    chips: pd.DataFrame
    revenue: pd.DataFrame


def _secret_list(name: str) -> list[str]:
    raw = None
    try:
        raw = st.secrets.get(name)
    except Exception:
        raw = None
    if raw is None:
        raw = os.getenv(name)
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        return [str(x).strip() for x in raw if str(x).strip()]
    text = str(raw).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            arr = json.loads(text)
            return [str(x).strip() for x in arr if str(x).strip()]
        except Exception:
            pass
    return [x.strip().strip('"').strip("'") for x in text.replace("\n", ",").split(",") if x.strip()]


def get_finmind_token() -> str | None:
    tokens = list(EMBEDDED_FINMIND_TOKENS) + _secret_list("FINMIND_TOKENS")
    single = None
    try:
        single = st.secrets.get("FINMIND_TOKEN")
    except Exception:
        single = None
    single = single or os.getenv("FINMIND_TOKEN")
    if single:
        tokens.append(str(single))
    tokens = [t for t in tokens if t]
    return random.choice(tokens) if tokens else None


def finmind_get(dataset: str, data_id: str | None = None, start_date: str | None = None, end_date: str | None = None, extra: dict[str, Any] | None = None) -> pd.DataFrame:
    params: dict[str, Any] = {"dataset": dataset}
    if data_id:
        params["data_id"] = data_id
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    token = get_finmind_token()
    if token:
        params["token"] = token
    if extra:
        params.update(extra)
    r = requests.get(FINMIND_API_URL, params=params, timeout=25)
    r.raise_for_status()
    payload = r.json()
    data = payload.get("data", [])
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)


@st.cache_data(ttl=6 * 60 * 60)
def load_stock_info() -> pd.DataFrame:
    try:
        return finmind_get("TaiwanStockInfo")
    except Exception:
        return pd.DataFrame()


def resolve_stock(query: str) -> tuple[str, str, str]:
    q = str(query).strip()
    if not q:
        return "2330", "台積電", "半導體業"
    info = load_stock_info()
    if not info.empty:
        for c in ["stock_id", "stock_name", "industry_category"]:
            if c not in info.columns:
                info[c] = ""
        hit = info[(info["stock_id"].astype(str) == q) | (info["stock_name"].astype(str) == q)]
        if hit.empty:
            hit = info[info["stock_name"].astype(str).str.contains(q, na=False, regex=False)]
        if not hit.empty:
            row = hit.iloc[0]
            return str(row.get("stock_id", q)), str(row.get("stock_name", q)), str(row.get("industry_category", ""))
    return q, q, ""


def to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def ema(values: pd.Series, span: int) -> pd.Series:
    return values.ewm(span=span, adjust=False).mean()


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out.rename(columns={"max": "high", "min": "low", "Trading_Volume": "volume"})
    for col in ["open", "high", "low", "close", "volume", "Trading_money", "spread"]:
        if col in out.columns:
            out[col] = to_num(out[col])
    out = out.sort_values("date").reset_index(drop=True)
    out["ma5"] = out["close"].rolling(5).mean()
    out["ma20"] = out["close"].rolling(20).mean()
    out["ma60"] = out["close"].rolling(60).mean()
    out["bb_mid"] = out["ma20"]
    out["bb_std"] = out["close"].rolling(20).std()
    out["bb_upper"] = out["bb_mid"] + 2 * out["bb_std"]
    out["bb_lower"] = out["bb_mid"] - 2 * out["bb_std"]

    diff = out["close"].diff()
    gain = diff.clip(lower=0)
    loss = -diff.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    out["rsi"] = 100 - 100 / (1 + rs)
    out.loc[avg_loss == 0, "rsi"] = 100

    out["ema12"] = ema(out["close"], 12)
    out["ema26"] = ema(out["close"], 26)
    out["macd_dif"] = out["ema12"] - out["ema26"]
    out["macd_dea"] = ema(out["macd_dif"], 9)
    out["macd_hist"] = (out["macd_dif"] - out["macd_dea"]) * 2

    low9 = out["low"].rolling(9).min()
    high9 = out["high"].rolling(9).max()
    rsv = ((out["close"] - low9) / (high9 - low9).replace(0, pd.NA) * 100).fillna(50)
    k_vals, d_vals = [], []
    k, d = 50.0, 50.0
    for val in rsv:
        k = (2 / 3) * k + (1 / 3) * float(val)
        d = (2 / 3) * d + (1 / 3) * k
        k_vals.append(k)
        d_vals.append(d)
    out["k"] = k_vals
    out["d"] = d_vals
    out["is_up"] = out["close"] >= out["open"]
    return out


@st.cache_data(ttl=15 * 60, show_spinner=False)
def fetch_stock_bundle(query: str) -> StockBundle:
    stock_id, stock_name, industry = resolve_stock(query)
    end = date.today()
    start_150 = end - timedelta(days=190)
    start_40 = end - timedelta(days=45)
    start_365 = end - timedelta(days=480)
    price = finmind_get("TaiwanStockPrice", data_id=stock_id, start_date=str(start_150), end_date=str(end))
    if price.empty:
        raise RuntimeError(f"找不到 {query} 的股價資料，請確認股票代號或名稱。")
    price = calculate_indicators(price).tail(110).reset_index(drop=True)
    chips = finmind_get("TaiwanStockInstitutionalInvestorsBuySell", data_id=stock_id, start_date=str(start_40), end_date=str(end))
    revenue = finmind_get("TaiwanStockMonthRevenue", data_id=stock_id, start_date=str(start_365), end_date=str(end))
    return StockBundle(stock_id=stock_id, stock_name=stock_name, industry=industry, prices=price, chips=chips, revenue=revenue)


def aggregate_chips(chips: pd.DataFrame, price: pd.DataFrame) -> pd.DataFrame:
    if chips.empty:
        return pd.DataFrame(columns=["date", "foreign", "trust", "dealer", "total", "price"])
    df = chips.copy()
    for c in ["buy", "sell"]:
        df[c] = to_num(df.get(c, pd.Series(dtype=float))).fillna(0)
    df["net"] = (df["buy"] - df["sell"]) / 1000
    out: dict[str, dict[str, float | str]] = {}
    for _, r in df.iterrows():
        d = str(r.get("date", ""))
        if not d:
            continue
        if d not in out:
            out[d] = {"date": d, "foreign": 0.0, "trust": 0.0, "dealer": 0.0}
        name = str(r.get("name", ""))
        net = float(r.get("net", 0))
        if "Foreign" in name or "外資" in name:
            out[d]["foreign"] = float(out[d]["foreign"]) + net
        elif "Trust" in name or "投信" in name:
            out[d]["trust"] = float(out[d]["trust"]) + net
        elif "Dealer" in name or "自營" in name:
            out[d]["dealer"] = float(out[d]["dealer"]) + net
    res = pd.DataFrame(out.values()).sort_values("date").tail(10)
    if res.empty:
        return res
    res["total"] = res[["foreign", "trust", "dealer"]].sum(axis=1)
    price_map = price.set_index("date")["close"].to_dict() if "date" in price.columns else {}
    res["price"] = res["date"].map(price_map)
    for c in ["foreign", "trust", "dealer", "total"]:
        res[c] = res[c].round(0).astype(int)
    return res.reset_index(drop=True)


def latest_revenue(revenue: pd.DataFrame) -> dict[str, Any]:
    blank = {"revenue": "-", "yoy": "-", "mom": "-", "period": "-"}
    if revenue.empty:
        return blank
    df = revenue.copy()
    rev_col = next((c for c in ["revenue", "營業收入-當月營收", "當月營收", "monthly_revenue"] if c in df.columns), None)
    if rev_col is None:
        return blank
    df["_revenue"] = pd.to_numeric(df[rev_col].astype(str).str.replace(",", "", regex=False).str.replace("--", "", regex=False), errors="coerce")
    if {"revenue_year", "revenue_month"}.issubset(df.columns):
        df["_year"] = pd.to_numeric(df["revenue_year"], errors="coerce")
        df["_month"] = pd.to_numeric(df["revenue_month"], errors="coerce")
    else:
        dt = pd.to_datetime(df.get("date"), errors="coerce") if "date" in df.columns else pd.Series(pd.NaT, index=df.index)
        df["_year"] = dt.dt.year
        df["_month"] = dt.dt.month
    df = df.dropna(subset=["_revenue", "_year", "_month"]).copy()
    if df.empty:
        return blank
    df["_year"] = df["_year"].astype(int)
    df["_month"] = df["_month"].astype(int)
    df = df[(df["_month"] >= 1) & (df["_month"] <= 12)]
    if df.empty:
        return blank
    df["_period_no"] = df["_year"] * 12 + df["_month"]
    df = df.sort_values(["_period_no"]).drop_duplicates("_period_no", keep="last").reset_index(drop=True)
    row = df.iloc[-1]
    cur_rev = float(row["_revenue"])
    year = int(row["_year"])
    month = int(row["_month"])
    rev_str = f"{cur_rev / 100000000:,.2f} 億"

    def pct(cur: float, base: Any) -> str:
        try:
            base_f = float(base)
            if not math.isfinite(base_f) or base_f == 0:
                return "-"
            return f"{(cur / base_f - 1) * 100:+.2f}%"
        except Exception:
            return "-"

    prev_rows = df[df["_period_no"] == int(row["_period_no"]) - 1]
    yoy_rows = df[df["_period_no"] == int(row["_period_no"]) - 12]
    return {"revenue": rev_str, "yoy": pct(cur_rev, yoy_rows["_revenue"].iloc[-1] if not yoy_rows.empty else None), "mom": pct(cur_rev, prev_rows["_revenue"].iloc[-1] if not prev_rows.empty else None), "period": f"{year}-{month:02d}"}


def round_tick(x: float) -> float:
    if not math.isfinite(x):
        return x
    if x >= 1000: step = 5
    elif x >= 500: step = 1
    elif x >= 100: step = 0.5
    elif x >= 50: step = 0.1
    elif x >= 10: step = 0.05
    else: step = 0.01
    return round(round(x / step) * step, 2)


def score_and_summary(bundle: StockBundle, chip10: pd.DataFrame) -> dict[str, Any]:
    p = bundle.prices
    latest = p.iloc[-1]
    close = float(latest["close"])
    score = 50
    reasons: list[str] = []
    if pd.notna(latest.get("ma5")) and pd.notna(latest.get("ma20")) and close > latest["ma5"] > latest["ma20"]:
        score += 18; reasons.append("均線多頭排列")
    elif pd.notna(latest.get("ma20")) and close < latest["ma20"]:
        score -= 12; reasons.append("跌破月線")
    if pd.notna(latest.get("ma60")) and close > latest["ma60"]: score += 8
    rsi = float(latest.get("rsi", 50) or 50)
    if 50 <= rsi <= 70:
        score += 10; reasons.append("RSI 位於偏多區")
    elif rsi > 78:
        score -= 8; reasons.append("RSI 過熱")
    elif rsi < 40:
        score -= 8; reasons.append("RSI 偏弱")
    if float(latest.get("macd_dif", 0)) > float(latest.get("macd_dea", 0)):
        score += 10; reasons.append("MACD 多頭")
    else:
        score -= 6
    if float(latest.get("volume", 0)) > float(p["volume"].tail(20).mean() or 0) * 1.25:
        score += 8; reasons.append("放量")
    chip_total = int(chip10["total"].sum()) if not chip10.empty else 0
    if chip_total > 0:
        score += min(12, chip_total / 5000); reasons.append("法人近10日買超")
    elif chip_total < 0:
        score -= min(12, abs(chip_total) / 5000); reasons.append("法人近10日賣超")
    score = int(max(0, min(100, round(score))))
    status = "偏多" if score >= 70 else "中性" if score >= 45 else "偏空"
    last20 = p.tail(20)
    resistance = round_tick(float(last20["high"].max()))
    support = round_tick(float(last20["low"].min()))
    ma20 = round_tick(float(latest.get("ma20", close))) if pd.notna(latest.get("ma20")) else support
    stop = round_tick(min(support, close * 0.96))
    entry = round_tick(max(close, float(latest.get("high", close))) * 1.005)
    target = round_tick(entry * 1.04)
    return {"score": score, "status": status, "reasons": reasons[:4] or ["資料不足"], "trend": "多頭" if close > float(latest.get("ma20", close)) else "偏弱", "macd_status": "多頭擴張" if float(latest.get("macd_dif", 0)) > float(latest.get("macd_dea", 0)) and float(latest.get("macd_hist", 0)) > 0 else "中性/轉弱", "volume_status": "放量" if float(latest.get("volume", 0)) > float(p["volume"].tail(20).mean() or 0) * 1.25 else "持平", "levels": {"pressure": f"{resistance:g}", "support": f"{support:g} ~ {ma20:g}", "strong": f"{support:g}", "stop": f"{stop:g}", "entry": f"{entry:g}", "target": f"{target:g}"}}


def fallback_ai(bundle: StockBundle, chip10: pd.DataFrame, qs: dict[str, Any]) -> dict[str, Any]:
    latest = bundle.prices.iloc[-1]
    status = qs["status"]
    action = "觀望" if status == "中性" else "買" if status == "偏多" else "賣"
    return {"tag": {"action": action, "reason": f"量化分數 {qs['score']} / 100，{status}"}, "techConclusion": f"趨勢方向 {qs['trend']}，RSI {float(latest.get('rsi', 0)):.2f}，MACD {qs['macd_status']}。", "chipConclusion": f"近10日法人合計 {int(chip10['total'].sum()) if not chip10.empty else 0:,} 張，籌碼面以資料為準。", "suggestions": [f"條件進場價：站上 {qs['levels']['entry']} 且量能放大，再列入短線觀察。", f"支撐區：{qs['levels']['support']}，跌破不急著攤平。", f"停損參考：{qs['levels']['stop']}，失守代表短線結構轉弱。", f"第一目標：{qs['levels']['target']}，接近目標需觀察量能是否延續。"], "levels": qs["levels"], "paths": [{"type": "上漲", "title": f"若站穩 {qs['levels']['entry']}，可觀察是否挑戰 {qs['levels']['target']}。"}, {"type": "回檔", "title": f"若回測 {qs['levels']['support']} 不破，屬偏多整理。"}, {"type": "轉弱", "title": f"若跌破 {qs['levels']['stop']}，短線轉弱應降部位。"}], "midTerm": ["追蹤月線與季線是否維持向上。", "留意營收年增率與法人籌碼是否同步改善。"], "warning": "本報告僅供研究參考，不構成投資建議。若短線量能急縮或跌破停損價，需降低假設強度。", "ratings": {"trend": 4 if qs['status'] == '偏多' else 3, "tech": 4 if qs['score'] >= 70 else 3, "chip": 4 if (not chip10.empty and chip10['total'].sum() > 0) else 3, "diff": 3}, "verdict": f"{bundle.stock_name}（{bundle.stock_id}）目前整體狀態為 {status}，優先依條件價與風控操作。", "news": []}


def get_google_keys() -> list[str]:
    keys = list(EMBEDDED_GOOGLE_API_KEYS) + _secret_list("GOOGLE_API_KEYS")
    single = None
    try:
        single = st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        single = None
    single = single or os.getenv("GOOGLE_API_KEY")
    if single:
        keys.append(str(single).strip())
    seen = set(); cleaned = []
    for key in keys:
        key = str(key).strip()
        if key and key not in seen:
            cleaned.append(key); seen.add(key)
    random.shuffle(cleaned)
    return cleaned


def _compact_gemini_error(exc: Exception | None) -> str:
    msg = str(exc or "")
    if "429" in msg or "Too Many Requests" in msg: return "Google Gemini API 額度或速率限制"
    if "403" in msg: return "Google Gemini API 權限或 key 限制"
    if "404" in msg: return "Google Gemini 模型名稱可能不可用"
    if not msg: return "Google Gemini 暫時無法回應"
    return "Google Gemini 呼叫失敗"


def _extract_json(text: str) -> dict[str, Any]:
    text = (text or "").replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, flags=re.S)
        if not m:
            raise
        return json.loads(m.group(0))


def _gemini_request(prompt: str, with_search: bool = False) -> dict[str, Any]:
    keys = get_google_keys()
    if not keys:
        raise RuntimeError("沒有可用的 Google API key")
    configured_model = None
    try:
        configured_model = st.secrets.get("GOOGLE_MODEL")
    except Exception:
        configured_model = None
    configured_model = configured_model or os.getenv("GOOGLE_MODEL")
    models = [configured_model] if configured_model else []
    # 多模型備援：避免單一 preview / flash 名稱不可用時，看起來像按鈕沒反應。
    models += ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    models = [m for i, m in enumerate(models) if m and m not in models[:i]]

    last_exc = None
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        base_body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.25},
        }
        tool_options = [True, False] if with_search else [False]
        for use_tool in tool_options:
            body = dict(base_body)
            if use_tool:
                body["tools"] = [{"google_search": {}}]
            for key_idx, key in enumerate(keys, start=1):
                try:
                    r = requests.post(url, params={"key": key}, json=body, timeout=60)
                    r.raise_for_status()
                    result = r.json()
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                    data = _extract_json(text)
                    data["_ai_key_status"] = f"Gemini 已啟用；模型 {model}；本次使用 API key 池第 {key_idx} 組。"
                    return data
                except Exception as exc:
                    last_exc = exc
                    continue
    raise RuntimeError(_compact_gemini_error(last_exc))


def call_gemini_detail(bundle: StockBundle, chip10: pd.DataFrame, qs: dict[str, Any], base_ai: dict[str, Any]) -> dict[str, Any]:
    latest = bundle.prices.iloc[-1]
    payload = {"stock": {"id": bundle.stock_id, "name": bundle.stock_name, "industry": bundle.industry}, "latest": {"close": latest.get("close"), "spread": latest.get("spread"), "volume": latest.get("volume"), "ma5": latest.get("ma5"), "ma20": latest.get("ma20"), "ma60": latest.get("ma60"), "rsi": latest.get("rsi"), "k": latest.get("k"), "d": latest.get("d"), "macd_dif": latest.get("macd_dif"), "macd_dea": latest.get("macd_dea")}, "chip10": chip10.tail(10).to_dict("records") if not chip10.empty else [], "quant": qs}
    prompt = f"""
你是一位台股分析助理。請根據下列資料，用繁體中文輸出 JSON，不要輸出 markdown。
重點：先給出整體結論，再生成技術面結論、籌碼面結論、短線建議、三條可能路徑、風險提醒。
不要搜尋新聞。
JSON schema:
{{
  "tag": {{"action":"買/賣/觀望", "reason":"一句短評"}},
  "verdict":"先給出一段清楚的分析文字結論",
  "techConclusion":"一句話總結技術面",
  "chipConclusion":"一句話總結籌碼面",
  "suggestions":["建議1","建議2","建議3","建議4"],
  "levels": {{"pressure":"壓力價位區間", "support":"支撐價位區間", "strong":"強支撐價位", "stop":"停損參考價", "entry":"條件進場價", "target":"第一目標價"}},
  "paths":[{{"type":"上漲", "title":"..."}}, {{"type":"回檔", "title":"..."}}, {{"type":"轉弱", "title":"..."}}],
  "warning":"風險提醒內容",
  "ratings": {{"trend":1, "tech":1, "chip":1, "diff":1}}
}}
資料：{json.dumps(payload, ensure_ascii=False, default=str)}
""".strip()
    data = _gemini_request(prompt, with_search=False)
    merged = dict(base_ai)
    merged.update(data)
    if "levels" in data and isinstance(data["levels"], dict):
        lvl = dict(base_ai.get("levels", {})); lvl.update(data["levels"]); merged["levels"] = lvl
    return merged


def fetch_google_news_rss(bundle: StockBundle, limit: int = 6) -> list[dict[str, Any]]:
    """Public RSS fallback. This makes the news button visibly return content even if Gemini search is rate-limited."""
    query = quote_plus(f"{bundle.stock_name} {bundle.stock_id} 台股 OR 股票")
    url = f"https://news.google.com/rss/search?q={query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall(".//item")[:limit]:
            title = item.findtext("title", default="").strip()
            pub = item.findtext("pubDate", default="").strip()
            source_el = item.find("source")
            source = source_el.text.strip() if source_el is not None and source_el.text else "Google News"
            if title:
                items.append({"title": title, "source": source, "date": pub, "summary": "RSS 抓取結果；按 AI 新聞抓取會優先顯示可用新聞，Gemini 可用時再輔助整理。"})
        return items
    except Exception:
        return []


def call_gemini_news(bundle: StockBundle, qs: dict[str, Any]) -> list[dict[str, Any]]:
    rss_news = fetch_google_news_rss(bundle, limit=6)
    payload = {"stock": {"id": bundle.stock_id, "name": bundle.stock_name, "industry": bundle.industry}, "quant": qs, "rss_news": rss_news}
    prompt = f"""
請使用繁體中文，根據提供的 RSS 新聞候選與股票資料，整理這檔台股最近 4 則重要新聞。只輸出 JSON，不要輸出 markdown。
若 RSS 候選為空，請回傳空陣列，不要捏造新聞。
JSON schema: {{"news":[{{"title":"新聞標題","source":"媒體來源","date":"發布時間","summary":"一句話摘要"}}]}}
資料：{json.dumps(payload, ensure_ascii=False, default=str)}
""".strip()
    try:
        data = _gemini_request(prompt, with_search=False)
        news = data.get("news", []) if isinstance(data, dict) else []
        return news or rss_news[:4]
    except Exception:
        # Gemini 失敗時仍顯示 RSS 結果，避免使用者覺得按鈕沒反應。
        return rss_news[:4]


def fmt_num(x: Any, digits: int = 2) -> str:
    try:
        v = float(x)
        return f"{v:,.{digits}f}" if abs(v) < 1000 else f"{v:,.0f}"
    except Exception:
        return "-"


def metric(label: str, value: str, note: str = "", tone: str = "warm", value_kind: str = "", note_kind: str = "", value_class: str = "") -> None:
    tone_class = {"warm":"metric-warm", "cool":"metric-cool", "soft":"metric-soft", "sand":"metric-sand", "stone":"metric-stone"}.get(tone, "metric-warm")
    dynamic_class = f" val-{value_kind}" if value_kind in ["pos", "neg"] else ""
    note_class_css = f" note-{note_kind}" if note_kind in ["pos", "neg"] else ""
    extra_value_class = f" {value_class}" if value_class else ""
    st.markdown(f"<div class='metric-card {tone_class}'><div class='metric-label'>{label}</div><div class='metric-value{dynamic_class}{extra_value_class}'>{value}</div><div class='metric-note{note_class_css}'>{note}</div></div>", unsafe_allow_html=True)


def badge(text: str, kind: str = "mid") -> str:
    cls = {"pos":"badge-pos", "neg":"badge-neg", "mid":"badge-mid", "info":"badge-info"}.get(kind, "badge-mid")
    return f"<span class='badge {cls}'>{text}</span>"


def section_title(icon: str, text: str) -> str:
    return f"<div class='section-title'><span class='title-stick'></span><span>{icon}</span><span>{text}</span></div>"


def plot_technical(prices: pd.DataFrame) -> go.Figure:
    df = prices.copy()
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.035, row_heights=[0.48,0.16,0.18,0.18], subplot_titles=("日 K 線（含布林通道 / 均線）","成交量","RSI / KD","MACD"))
    inc, dec = "#c94d42", "#4f8a61"
    fig.add_trace(go.Candlestick(x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], increasing_line_color=inc, decreasing_line_color=dec, name="K線"), row=1, col=1)
    for col, name, color in [("ma5", "MA5", "#b89d6a"), ("ma20", "MA20", "#7c968b"), ("ma60", "MA60", "#ad8d80"), ("bb_upper", "BB上緣", "#bcb1a0"), ("bb_lower", "BB下緣", "#bcb1a0")]:
        if col in df:
            fig.add_trace(go.Scatter(x=df["date"], y=df[col], mode="lines", name=name, line=dict(color=color, width=1.4, dash="dot" if "BB" in name else None)), row=1, col=1)
    colors = [inc if bool(v) else dec for v in df["is_up"]]
    fig.add_trace(go.Bar(x=df["date"], y=df["volume"] / 1000, name="成交量(千張)", marker_color=colors), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["rsi"], mode="lines", name="RSI", line=dict(color="#b89d6a", width=1.6)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["k"], mode="lines", name="K", line=dict(color="#7c968b", width=1.3)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["d"], mode="lines", name="D", line=dict(color="#ad8d80", width=1.3)), row=3, col=1)
    fig.add_hline(y=80, line_dash="dash", line_color="#e0c8c5", row=3, col=1)
    fig.add_hline(y=20, line_dash="dash", line_color="#c9ddcf", row=3, col=1)
    hist_colors = [inc if float(v or 0) >= 0 else dec for v in df["macd_hist"]]
    fig.add_trace(go.Bar(x=df["date"], y=df["macd_hist"], name="MACD柱", marker_color=hist_colors), row=4, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["macd_dif"], mode="lines", name="DIF", line=dict(color="#7c968b", width=1.5)), row=4, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["macd_dea"], mode="lines", name="DEA", line=dict(color="#b89d6a", width=1.5)), row=4, col=1)
    fig.update_layout(height=760, template="plotly_white", margin=dict(l=20,r=20,t=45,b=20), xaxis_rangeslider_visible=False, legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center"), paper_bgcolor="#fbf8f2", plot_bgcolor="#fbf8f2")
    fig.update_yaxes(showgrid=True, gridcolor="#efe6d8")
    fig.update_xaxes(showgrid=False)
    return fig


def plot_chips(chip10: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if chip10.empty:
        return fig
    fig.add_trace(go.Bar(x=chip10["date"], y=chip10["foreign"], name="外資", marker_color="#7b8fa6"), secondary_y=False)
    fig.add_trace(go.Bar(x=chip10["date"], y=chip10["trust"], name="投信", marker_color="#b3946d"), secondary_y=False)
    fig.add_trace(go.Bar(x=chip10["date"], y=chip10["dealer"], name="自營商", marker_color="#9a8395"), secondary_y=False)
    if "price" in chip10.columns:
        fig.add_trace(go.Scatter(x=chip10["date"], y=chip10["price"], name="股價", mode="lines+markers", line=dict(color="#706b66", width=2)), secondary_y=True)
    fig.update_layout(height=360, barmode="relative", template="plotly_white", margin=dict(l=20,r=20,t=20,b=20), paper_bgcolor="#fbf8f2", plot_bgcolor="#fbf8f2", legend=dict(orientation="h"))
    fig.update_yaxes(title_text="買賣超（千張）", secondary_y=False)
    fig.update_yaxes(title_text="股價", secondary_y=True)
    return fig


def stars(n: Any) -> str:
    try:
        n = int(float(n))
    except Exception:
        n = 3
    n = max(1, min(5, n))
    return "★" * n + "☆" * (5 - n)


def render_app() -> None:
    st.markdown(f"<div class='hero'><div class='hero-title'>📊 {APP_TITLE}</div><div class='hero-sub'>輸入股票代號或中文名稱，串接 FinMind 股價 / 法人籌碼資料。AI 詳細分析與 AI 新聞抓取採獨立按鈕觸發，預設不主動連接 API。資料僅供研究，不構成投資建議。</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='search-card'>", unsafe_allow_html=True)
    q_label, q_box = st.columns([1, 5])
    with q_label:
        st.markdown("<div class='small-muted' style='padding-top:.35rem;font-weight:700'>股票代號或中文名稱</div>", unsafe_allow_html=True)
    with q_box:
        q = st.text_input("股票代號或中文名稱", value=st.session_state.get("query", "2330"), label_visibility="collapsed", placeholder="例如：2330、台積電、友達")
    mode_col, run_col = st.columns([2.6, 1])
    with mode_col:
        ai_mode = st.selectbox(
            "分析模式",
            ["數據分析｜不呼叫 API", "數據 + AI 詳細分析", "數據 + AI 新聞抓取", "數據 + AI 詳細 + 新聞"],
            index=0,
            key="analysis_mode",
        )
    with run_col:
        st.write("")
        st.markdown("<div class='top-btn-row primary'>", unsafe_allow_html=True)
        run = st.button("執行分析", use_container_width=True, key="btn_run_all")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='footer-tip'>新版架構改成『選模式 → 執行分析』，避免 Streamlit 按鈕 rerun 後看起來沒反應。AI 若失敗，區塊會顯示原因並保留規則版分析。</div></div>", unsafe_allow_html=True)

    q_changed = q != st.session_state.get("query")
    run_detail = run and ("詳細" in ai_mode)
    run_news = run and ("新聞" in ai_mode)
    if run or "last_bundle" not in st.session_state or q_changed:
        st.session_state["query"] = q
        st.session_state["error"] = None
        st.session_state["ai_notice"] = None
        st.session_state["news_notice"] = None
        with st.spinner("抓取 FinMind 資料並計算技術指標..."):
            try:
                bundle = fetch_stock_bundle(q)
                chip10 = aggregate_chips(bundle.chips, bundle.prices)
                qs = score_and_summary(bundle, chip10)
                ai = fallback_ai(bundle, chip10, qs)
                st.session_state["last_bundle"] = bundle
                st.session_state["last_chips"] = chip10
                st.session_state["last_qs"] = qs
                st.session_state["last_ai"] = ai
                st.session_state["detail_loaded"] = False
                st.session_state["news_loaded"] = False
            except Exception as exc:
                st.session_state["error"] = str(exc)

    if st.session_state.get("error"):
        st.error(st.session_state["error"])
        return

    bundle: StockBundle | None = st.session_state.get("last_bundle")
    if bundle is None:
        return
    chip10: pd.DataFrame = st.session_state["last_chips"]
    qs: dict[str, Any] = st.session_state["last_qs"]
    ai: dict[str, Any] = st.session_state["last_ai"]

    if run_detail:
        with st.spinner("Google Gemini 產生詳細分析中..."):
            try:
                ai = call_gemini_detail(bundle, chip10, qs, ai)
                st.session_state["last_ai"] = ai
                st.session_state["detail_loaded"] = True
                st.session_state["ai_notice"] = "AI 詳細分析已完成：" + ai.get("_ai_key_status", "Gemini 已回傳結果")
            except Exception as exc:
                st.session_state["ai_notice"] = f"{_compact_gemini_error(exc)}，目前維持規則版分析"

    if run_news:
        with st.spinner("抓取近期重要新聞中；Gemini 可用時會輔助整理..."):
            try:
                news = call_gemini_news(bundle, qs)
                ai = dict(st.session_state["last_ai"])
                ai["news"] = news
                st.session_state["last_ai"] = ai
                st.session_state["news_loaded"] = True
                st.session_state["news_notice"] = "新聞抓取已完成；Gemini 可用時已輔助整理，否則顯示 RSS 結果"
            except Exception as exc:
                st.session_state["news_notice"] = _compact_gemini_error(exc)

    ai = st.session_state["last_ai"]
    latest = bundle.prices.iloc[-1]
    prev_close = float(latest["close"] - (latest.get("spread", 0) or 0)) if pd.notna(latest.get("spread")) else float(bundle.prices.iloc[-2]["close"])
    pct = (float(latest["close"]) - prev_close) / prev_close * 100 if prev_close else 0
    up = pct >= 0
    rev = latest_revenue(bundle.revenue)

    st.markdown(f"## {bundle.stock_name}（{bundle.stock_id}）AI 分析報告")
    st.caption(f"產業：{bundle.industry or '-'} ｜ 報告生成：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 整體狀態：{qs['status']}")
    levels = ai.get("levels", qs["levels"])

    summary_text = ai.get("verdict") or fallback_ai(bundle, chip10, qs).get("verdict", "-")
    summary_sub = []
    summary_sub.append("目前為規則版數據分析" if not st.session_state.get("detail_loaded") else st.session_state.get("ai_notice", "AI 詳細分析已完成"))
    if st.session_state.get("news_loaded"):
        summary_sub.append(st.session_state.get("news_notice", "AI 新聞抓取已完成"))
    st.markdown(f"<div class='summary-box'><div class='summary-title'>先看分析文字結論</div><div class='summary-text'>{summary_text}</div><div class='summary-sub'>{' ｜ '.join(summary_sub)}</div></div>", unsafe_allow_html=True)

    # Move trade plan and path summary to the top for faster reading.
    st.markdown("<div class='section-card section-ai'>" + section_title("🧩", "操作建議與可能路徑") , unsafe_allow_html=True)
    left_plan, right_path = st.columns([1, 1])
    with left_plan:
        st.markdown("**操作建議**")
        suggestions = ai.get("suggestions", [])
        if suggestions:
            st.markdown("<div class='action-grid'>" + "".join([f"<div class='action-item'>• {s}</div>" for s in suggestions[:4]]) + "</div>", unsafe_allow_html=True)
        else:
            st.write("目前沒有操作建議。")
    with right_path:
        st.markdown("**可能路徑與評分**")
        for p in ai.get("paths", [])[:3]:
            st.markdown(f"<div class='path-item'><span class='path-label'>{p.get('type','')}</span>{p.get('title','')}</div>", unsafe_allow_html=True)
        ratings = ai.get("ratings", {})
        st.markdown(
            f"<div class='action-grid'>"
            f"<div class='action-item'><b>股價趨勢</b><br>{stars(ratings.get('trend', 3))}</div>"
            f"<div class='action-item'><b>技術面</b><br>{stars(ratings.get('tech', 3))}</div>"
            f"<div class='action-item'><b>籌碼面</b><br>{stars(ratings.get('chip', 3))}</div>"
            f"<div class='action-item'><b>操作難度</b><br>{stars(ratings.get('diff', 3))}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # AI detail/news near top
    ai_left, ai_right = st.columns(2)
    with ai_left:
        st.markdown("<div class='ai-mini-box'>" + section_title("🧠", "AI 詳細分析") , unsafe_allow_html=True)
        if st.session_state.get("ai_notice"):
            notice_class = "status-warn" if "限制" in str(st.session_state.get("ai_notice")) or "失敗" in str(st.session_state.get("ai_notice")) else ""
            st.markdown(f"<div class='status-box {notice_class}'>{st.session_state.get('ai_notice')}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='status-box'>尚未執行 AI 詳細分析。按上方按鈕後，結果會顯示在這裡。</div>", unsafe_allow_html=True)
        st.write(ai.get("techConclusion", "尚未執行 AI 詳細分析，目前顯示規則版技術摘要。"))
        st.write(ai.get("chipConclusion", ""))
        st.markdown("<b>短線操作建議</b>", unsafe_allow_html=True)
        for s in ai.get("suggestions", [])[:3]:
            st.write(f"• {s}")
        st.markdown("</div>", unsafe_allow_html=True)
    with ai_right:
        st.markdown("<div class='ai-mini-box'>" + section_title("📰", "AI 新聞抓取") , unsafe_allow_html=True)
        if st.session_state.get("news_notice"):
            notice_class = "status-warn" if "限制" in str(st.session_state.get("news_notice")) or "失敗" in str(st.session_state.get("news_notice")) else ""
            st.markdown(f"<div class='status-box {notice_class}'>{st.session_state.get('news_notice')}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='status-box'>尚未執行 AI 新聞抓取。按上方按鈕後，新聞會顯示在這裡。</div>", unsafe_allow_html=True)
        news = ai.get("news", []) or []
        if news:
            for item in news[:3]:
                st.markdown(f"<div style='margin-bottom:.85rem'><div style='font-weight:800;line-height:1.6'>{item.get('title','')}</div><div class='small-muted'>{item.get('source','市場新聞')} ｜ {item.get('date','')}</div><div style='margin-top:.25rem'>{item.get('summary','')}</div></div><hr class='soft'>", unsafe_allow_html=True)
        else:
            st.write("尚未執行 AI 新聞抓取。若需要抓新聞，請按上方「AI 新聞抓取」按鈕。")
        st.markdown("</div>", unsafe_allow_html=True)

    # top metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        metric("即時收盤價", f"{float(latest['close']):g}", f"{'▲' if up else '▼'} {pct:+.2f}%", tone="warm", value_kind="pos" if up else "neg", note_kind="pos" if up else "neg")
    with m2:
        metric("成交量", f"{int(round(float(latest['volume']) / 1000)):,} 張", qs["volume_status"], tone="stone")
    with m3:
        metric("偏多分數", f"{qs['score']} / 100", ai.get("tag", {}).get("reason", ""), tone="soft", value_kind="pos" if qs['status']=="偏多" else ("neg" if qs['status']=="偏空" else ""))

    st.markdown(section_title("🚦", "警示燈號"), unsafe_allow_html=True)
    kinds = []
    for reason in qs["reasons"]:
        if any(x in reason for x in ["多頭", "買超", "放量"]): kinds.append("pos")
        elif any(x in reason for x in ["跌破", "賣超", "過熱", "偏弱"]): kinds.append("neg")
        else: kinds.append("mid")
    st.markdown("".join(badge(r, kinds[i] if i < len(kinds) else "mid") for i, r in enumerate(qs["reasons"])), unsafe_allow_html=True)

    t1, t2, t3, t4 = st.columns(4)
    with t1: metric("趨勢方向", qs["trend"], tone="sand", value_kind="pos" if qs['trend']=="多頭" else "neg")
    with t2: metric("RSI(14)", fmt_num(latest.get("rsi")), tone="cool")
    with t3: metric("MACD 狀態", qs["macd_status"], tone="soft", value_kind="pos" if "多頭" in qs['macd_status'] else "neg")
    with t4: metric("量能變化", qs["volume_status"], tone="stone")

    st.markdown("<div class='section-card section-tech'>" + section_title("📈", "技術圖表") , unsafe_allow_html=True)
    st.plotly_chart(plot_technical(bundle.prices), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card section-chip'>" + section_title("🏦", "籌碼面") , unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    foreign = int(chip10.iloc[-1]["foreign"]) if not chip10.empty else 0
    trust = int(chip10.iloc[-1]["trust"]) if not chip10.empty else 0
    dealer = int(chip10.iloc[-1]["dealer"]) if not chip10.empty else 0
    total = int(chip10.iloc[-1]["total"]) if not chip10.empty else 0
    with c1: metric("外資(千張)", f"{foreign:+,}", tone="cool", value_class="institution-foreign")
    with c2: metric("投信(千張)", f"{trust:+,}", tone="cool", value_class="institution-trust")
    with c3: metric("自營商(千張)", f"{dealer:+,}", tone="cool", value_class="institution-dealer")
    with c4: metric("合計(千張)", f"{total:+,}", tone="cool", value_class="institution-total")
    st.plotly_chart(plot_chips(chip10), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card section-fund'>" + section_title("📊", "基本面") , unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    with b1: metric("最新月營收", rev["revenue"], f"營收月份 {rev.get('period', '-')}", tone="sand")
    with b2: metric("YoY 年增率", rev["yoy"], tone="sand", value_kind="pos" if str(rev['yoy']).startswith('+') else ("neg" if str(rev['yoy']).startswith('-') else ""))
    with b3: metric("MoM 月增率", rev["mom"], tone="sand", value_kind="pos" if str(rev['mom']).startswith('+') else ("neg" if str(rev['mom']).startswith('-') else ""))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card section-neutral'>" + section_title("🎯", "關鍵價位") , unsafe_allow_html=True)
    l1, l2, l3, l4 = st.columns(4)
    with l1: metric("條件進場價", str(levels.get("entry", qs["levels"].get("entry"))), tone="warm")
    with l2: metric("壓力區", str(levels.get("pressure", qs["levels"].get("pressure"))), tone="warm")
    with l3: metric("支撐區", str(levels.get("support", qs["levels"].get("support"))), tone="warm")
    with l4: metric("停損參考", str(levels.get("stop", qs["levels"].get("stop"))), tone="warm")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card section-risk'>" + section_title("⚠️", "風險評估") , unsafe_allow_html=True)
    st.markdown(f"<div class='warn-box'>{ai.get('warning','投資有風險，請審慎評估。')}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("原始資料 / 除錯"):
        st.write("價格資料")
        st.dataframe(bundle.prices.tail(20), use_container_width=True)
        st.write("籌碼資料")
        st.dataframe(chip10, use_container_width=True)
        st.write("月營收資料")
        st.dataframe(bundle.revenue.tail(12), use_container_width=True)

    st.caption(f"📊資料來源：FinMind ｜ 🤖AI：Google Gemini（按鈕觸發） ｜ Build：{APP_BUILD} ｜ ⚠️本報告僅供研究參考，不構成投資建議。")


render_app()
