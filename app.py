from __future__ import annotations

import json
import math
import os
import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Iterable

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import streamlit as st

APP_TITLE = "台股 AI 個股分析"
APP_BUILD = "2026-07-03-revenue-volume-fix-v2"
FINMIND_API_URL = "https://api.finmindtrade.com/api/v4/data"

# Direct GitHub upload build: API pools are embedded per user request.
# Later, rotate these keys and move them to Streamlit Secrets for safer operation.
EMBEDDED_FINMIND_TOKENS = ['eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZnJlZW9uZXllYXJhaSIsImVtYWlsIjoiZnJlZW9uZXllYXJhaUBnbWFpbC5jb20ifQ.QrpcS4DVlqm7bdsL-bDmGdNTtg8HKzm2rrwJUtf7v24', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiaG9kaWRpZmlubWluZCIsImVtYWlsIjoiaG9kaWRpQGdtYWlsLmNvbSJ9._w1f1blFk5cVtxYkQdArSPuP2nMbcj0ecB5WUOCp1d8', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiaG9kaWRpIiwiZW1haWwiOiJnZW1pbmkyMDI1MTA4QGdtYWlsLmNvbSJ9.hvVPA_bI3YdsapZTQ5m4bJsAeR61z1NgcXBZlm2m4lw', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMjAyNWNoZW5jaGVuMjAyNSIsImVtYWlsIjoiMjAyNWNoZW5jaGVuMjAyNUBnbWFpbC5jb20ifQ.IcNKTcRbriGQOcRAH_y13Tif2aYxKjYv5cRtZVkoOHo']
EMBEDDED_GOOGLE_API_KEYS = ['AIzaSyD41KegJf4ZV1ZpNI2sd4Kd1nJT1HBL_LA', 'AIzaSyD0Mxqd9g8RmAMN6oOSAqi9p8UfudRO8bI', 'AIzaSyAU_Y8Og0wI6HtWLwRNRW7TTGYzyhBlRSY']

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
:root{
  --bg:#f5f1e9; --panel:#fffdf8; --panel2:#f8f3ea; --ink:#3b3833; --muted:#8a8176;
  --gold:#c8ab6a; --gold2:#a88745; --line:#e2d7c5; --red:#8f4248; --green:#3f6d57;
  --blue:#5f7f99; --purple:#9a7e95;
}
html, body, .stApp{background:var(--bg); color:var(--ink);}
.block-container{max-width:1280px; padding-top:1.2rem; padding-bottom:4rem;}
section[data-testid="stSidebar"]{display:none!important;} div[data-testid="collapsedControl"]{display:none!important;}
h1,h2,h3,h4{color:var(--ink); letter-spacing:.01em;}
.hero{background:linear-gradient(135deg,#fffdf8 0%,#f5efe2 100%); border:1px solid var(--line); border-top:5px solid var(--gold); border-radius:22px; padding:1.25rem 1.45rem; box-shadow:0 10px 32px rgba(80,60,30,.08); margin-bottom:1rem;}
.hero-title{font-size:2.25rem; font-weight:900; color:var(--ink); display:flex; align-items:center; gap:.6rem;}
.hero-sub{color:var(--muted); margin-top:.35rem; font-size:.95rem;}
.search-card{background:var(--panel); border:1px solid var(--line); border-radius:20px; padding:1rem 1.1rem; box-shadow:0 8px 22px rgba(80,60,30,.06); margin-bottom:1rem;}
.metric-card{background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:1rem 1.05rem; min-height:120px; box-shadow:0 8px 22px rgba(80,60,30,.05);}
.metric-label{color:var(--muted); font-size:.9rem; margin-bottom:.4rem;}
.metric-value{font-size:2rem; font-weight:900; color:var(--ink); line-height:1.2;}
.metric-note{color:var(--muted); font-size:.86rem; margin-top:.3rem;}
.badge{display:inline-flex; align-items:center; gap:.35rem; border:1px solid var(--line); border-radius:999px; padding:.35rem .75rem; background:#fff; font-weight:700; margin:.15rem .25rem .15rem 0;}
.badge-red{color:var(--red); border-color:#e5c5c7; background:#fff7f7}.badge-green{color:var(--green); border-color:#bdd7c8; background:#f4fbf7}.badge-gold{color:var(--gold2); border-color:#e3d1a6; background:#fffaf0}.badge-blue{color:var(--blue); border-color:#c8d5df; background:#f3f8fb}
.section{background:var(--panel); border:1px solid var(--line); border-radius:22px; padding:1.1rem 1.2rem; box-shadow:0 8px 26px rgba(80,60,30,.06); margin-bottom:1rem;}
.section-title{font-size:1.25rem; font-weight:900; color:var(--gold2); border-left:6px solid var(--gold); padding-left:.7rem; margin:.2rem 0 1rem;}
.ai-box{background:#fffaf0; border:1px solid #e2cd98; border-radius:22px; padding:1.15rem 1.2rem; line-height:1.8;}
.warn-box{background:#fff6f6; border:1px solid #e7c4c4; color:#6f3034; border-radius:16px; padding:.85rem 1rem; line-height:1.7;}
.small-muted{color:var(--muted); font-size:.88rem;}
.stTabs [data-baseweb="tab-list"]{gap:.4rem;}
.stTabs [data-baseweb="tab"]{background:#fffdf8; border:1px solid var(--line); border-radius:999px; padding:.55rem 1rem; color:var(--ink);}
.stTabs [aria-selected="true"]{background:#f7ead0!important; border-color:#c8ab6a!important; color:#6d5120!important;}
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
    """Read list-like secrets safely. Supports TOML list or comma/newline separated string."""
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
    # A JSON/TOML-ish list pasted as string.
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
    rename = {"max": "high", "min": "low", "Trading_Volume": "volume"}
    out = out.rename(columns=rename)
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
    """Return latest monthly revenue and calculated YoY/MoM.

    FinMind TaiwanStockMonthRevenue fields are usually:
    - revenue: monthly revenue amount in NTD
    - revenue_year: the revenue year, for example 2026
    - revenue_month: the revenue month, for example 5

    revenue_year / revenue_month are identifiers, NOT percentages. This function
    creates a YYYY-MM period from revenue_year + revenue_month first, then compares:
    - YoY: latest month vs same month last year
    - MoM: latest month vs previous month
    """
    blank = {"revenue": "-", "yoy": "-", "mom": "-", "period": "-"}
    if revenue.empty:
        return blank

    df = revenue.copy()

    # Find revenue column. Keep several fallbacks for manually uploaded CSV variants.
    rev_col = None
    for c in ["revenue", "營業收入-當月營收", "當月營收", "monthly_revenue"]:
        if c in df.columns:
            rev_col = c
            break
    if rev_col is None:
        return blank

    df["_revenue"] = (
        df[rev_col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("--", "", regex=False)
    )
    df["_revenue"] = pd.to_numeric(df["_revenue"], errors="coerce")

    # Prefer revenue_year/revenue_month, because FinMind date can be the publish
    # month while revenue_month is the actual operating month.
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

    # Deduplicate by month, keep latest row if there are revisions.
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

    # MoM: exact previous calendar month.
    prev_period = int(row["_period_no"]) - 1
    prev_rows = df[df["_period_no"] == prev_period]
    mom_base = prev_rows["_revenue"].iloc[-1] if not prev_rows.empty else None

    # YoY: same month previous year.
    yoy_period = int(row["_period_no"]) - 12
    yoy_rows = df[df["_period_no"] == yoy_period]
    yoy_base = yoy_rows["_revenue"].iloc[-1] if not yoy_rows.empty else None

    return {
        "revenue": rev_str,
        "yoy": pct(cur_rev, yoy_base),
        "mom": pct(cur_rev, mom_base),
        "period": f"{year}-{month:02d}",
    }

def round_tick(x: float) -> float:
    if not math.isfinite(x):
        return x
    if x >= 1000:
        step = 5
    elif x >= 500:
        step = 1
    elif x >= 100:
        step = 0.5
    elif x >= 50:
        step = 0.1
    elif x >= 10:
        step = 0.05
    else:
        step = 0.01
    return round(round(x / step) * step, 2)


def score_and_summary(bundle: StockBundle, chip10: pd.DataFrame) -> dict[str, Any]:
    p = bundle.prices
    latest = p.iloc[-1]
    prev = p.iloc[-2] if len(p) >= 2 else latest
    close = float(latest["close"])
    score = 50
    reasons: list[str] = []
    if pd.notna(latest.get("ma5")) and pd.notna(latest.get("ma20")) and close > latest["ma5"] > latest["ma20"]:
        score += 18; reasons.append("均線多頭排列")
    elif pd.notna(latest.get("ma20")) and close < latest["ma20"]:
        score -= 12; reasons.append("跌破月線")
    if pd.notna(latest.get("ma60")) and close > latest["ma60"]:
        score += 8
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
    return {
        "score": score,
        "status": status,
        "reasons": reasons[:4] or ["資料不足"],
        "trend": "多頭" if close > float(latest.get("ma20", close)) else "偏弱",
        "macd_status": "多頭擴張" if float(latest.get("macd_dif", 0)) > float(latest.get("macd_dea", 0)) and float(latest.get("macd_hist", 0)) > 0 else "中性/轉弱",
        "volume_status": "放量" if float(latest.get("volume", 0)) > float(p["volume"].tail(20).mean() or 0) * 1.25 else "持平",
        "levels": {"pressure": f"{resistance:g}", "support": f"{support:g} ~ {ma20:g}", "strong": f"{support:g}", "stop": f"{stop:g}", "entry": f"{entry:g}", "target": f"{target:g}"},
    }


def fallback_ai(bundle: StockBundle, chip10: pd.DataFrame, qs: dict[str, Any]) -> dict[str, Any]:
    latest = bundle.prices.iloc[-1]
    status = qs["status"]
    action = "觀望" if status == "中性" else "買" if status == "偏多" else "賣"
    return {
        "tag": {"action": action, "reason": f"量化分數 {qs['score']} / 100，{status}"},
        "techConclusion": f"趨勢方向 {qs['trend']}，RSI {float(latest.get('rsi', 0)):.2f}，MACD {qs['macd_status']}。",
        "chipConclusion": f"近10日法人合計 {int(chip10['total'].sum()) if not chip10.empty else 0:,} 張，籌碼面以資料為準。",
        "suggestions": [
            f"條件進場價：站上 {qs['levels']['entry']} 且量能放大，再列入短線觀察。",
            f"支撐區：{qs['levels']['support']}，跌破不急著攤平。",
            f"停損參考：{qs['levels']['stop']}，失守代表短線結構轉弱。",
            f"第一目標：{qs['levels']['target']}，接近目標需觀察量能是否延續。",
        ],
        "levels": qs["levels"],
        "paths": [
            {"type": "上漲", "title": f"若站穩 {qs['levels']['entry']}，可觀察是否挑戰 {qs['levels']['target']}。"},
            {"type": "回檔", "title": f"若回測 {qs['levels']['support']} 不破，屬偏多整理。"},
            {"type": "轉弱", "title": f"若跌破 {qs['levels']['stop']}，短線轉弱應降部位。"},
        ],
        "midTerm": ["追蹤月線與季線是否維持向上。", "留意營收年增率與法人籌碼是否同步改善。"],
        "warning": "本報告僅供研究參考，不構成投資建議。若短線量能急縮或跌破停損價，需降低假設強度。",
        "ratings": {"trend": 4 if qs['status'] == '偏多' else 3, "tech": 4 if qs['score'] >= 70 else 3, "chip": 4 if (not chip10.empty and chip10['total'].sum() > 0) else 3, "diff": 3},
        "verdict": f"{bundle.stock_name}（{bundle.stock_id}）目前整體狀態為 {status}，優先依條件價與風控操作。",
        "news": [],
    }


def get_google_keys() -> list[str]:
    """Read Gemini API keys as a pool.

    Supported Streamlit Secrets / env formats:
    - GOOGLE_API_KEYS = ["key1", "key2", "key3"]
    - GOOGLE_API_KEYS = "key1,key2,key3"
    - GOOGLE_API_KEY = "single_key"
    The app will rotate keys and try the next key automatically if one fails.
    """
    keys = list(EMBEDDED_GOOGLE_API_KEYS) + _secret_list("GOOGLE_API_KEYS")
    single = None
    try:
        single = st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        single = None
    single = single or os.getenv("GOOGLE_API_KEY")
    if single:
        keys.append(str(single).strip())
    # Preserve order while removing blanks/duplicates.
    seen: set[str] = set()
    cleaned: list[str] = []
    for key in keys:
        key = str(key).strip()
        if key and key not in seen:
            cleaned.append(key)
            seen.add(key)
    random.shuffle(cleaned)
    return cleaned


def call_gemini(bundle: StockBundle, chip10: pd.DataFrame, qs: dict[str, Any]) -> dict[str, Any]:
    keys = get_google_keys()
    if not keys:
        return fallback_ai(bundle, chip10, qs)
    latest = bundle.prices.iloc[-1]
    recent_chips = chip10.tail(10).to_dict("records") if not chip10.empty else []
    model = None
    try:
        model = st.secrets.get("GOOGLE_MODEL")
    except Exception:
        model = None
    model = model or os.getenv("GOOGLE_MODEL") or "gemini-2.5-flash"
    payload = {
        "stock": {"id": bundle.stock_id, "name": bundle.stock_name, "industry": bundle.industry},
        "latest": {"close": latest.get("close"), "spread": latest.get("spread"), "volume": latest.get("volume"), "ma5": latest.get("ma5"), "ma20": latest.get("ma20"), "ma60": latest.get("ma60"), "rsi": latest.get("rsi"), "k": latest.get("k"), "d": latest.get("d"), "macd_dif": latest.get("macd_dif"), "macd_dea": latest.get("macd_dea")},
        "chip10": recent_chips,
        "quant": qs,
    }
    prompt = f"""
你是一位實戰經驗豐富的台股分析助理。根據下列真實資料，產出台股個股分析 JSON。
要求：
1. 使用繁體中文。
2. 不要保證漲跌，不要使用必漲、穩賺等字眼。
3. 必須包含具體進場條件、支撐、壓力、停損、風險。
4. 若可用搜尋能力，整理最近 4 則重要新聞；若沒有搜尋到，news 回傳空陣列。
5. 僅輸出 JSON，不要 Markdown。
JSON schema:
{{
  "tag": {{"action":"買/賣/觀望", "reason":"一句短評"}},
  "techConclusion":"一句話總結技術面",
  "chipConclusion":"一句話總結籌碼面",
  "suggestions":["具體建議1","具體建議2","具體建議3","具體建議4"],
  "levels": {{"pressure":"壓力價位區間", "support":"支撐價位區間", "strong":"強支撐價位", "stop":"停損參考價", "entry":"條件進場價", "target":"第一目標價"}},
  "paths":[{{"type":"上漲", "title":"..."}}, {{"type":"回檔", "title":"..."}}, {{"type":"轉弱", "title":"..."}}],
  "midTerm":["中長線觀點1","中長線觀點2"],
  "warning":"風險提醒內容",
  "ratings": {{"trend":1, "tech":1, "chip":1, "diff":1}},
  "verdict":"綜合評估結論",
  "news":[{{"title":"新聞標題", "source":"媒體來源", "date":"發布時間"}}]
}}
資料：{json.dumps(payload, ensure_ascii=False, default=str)}
""".strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.35},
    }
    # Some Gemini models support grounding with google_search. If rejected, fallback to no tool.
    last_exc: Exception | None = None
    for key in keys:
        for with_tool in [True, False]:
            try:
                if with_tool:
                    body["tools"] = [{"google_search": {}}]
                else:
                    body.pop("tools", None)
                r = requests.post(url, params={"key": key}, json=body, timeout=60)
                r.raise_for_status()
                result = r.json()
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                text = text.replace("```json", "").replace("```", "").strip()
                data = json.loads(text)
                base = fallback_ai(bundle, chip10, qs)
                base.update(data)
                if "levels" in data and isinstance(data["levels"], dict):
                    lvl = base.get("levels", {})
                    lvl.update(data["levels"])
                    base["levels"] = lvl
                base["_ai_key_status"] = f"Gemini 已啟用；本次使用 API key 池第 {keys.index(key) + 1} 組。"
                return base
            except Exception as exc:
                last_exc = exc
                continue
    res = fallback_ai(bundle, chip10, qs)
    def _compact_gemini_error(exc: Exception | None) -> str:
        msg = str(exc or "")
        if "429" in msg or "Too Many Requests" in msg:
            return "Google Gemini API 額度或速率限制，已改用規則版分析"
        if "403" in msg:
            return "Google Gemini API 權限或 key 限制，已改用規則版分析"
        if "404" in msg:
            return "Google Gemini 模型名稱可能不可用，已改用規則版分析"
        if not msg:
            return "Google Gemini 暫時無法回應，已改用規則版分析"
        return "Google Gemini 呼叫失敗，已改用規則版分析"

    res["verdict"] = res["verdict"] + f"（{_compact_gemini_error(last_exc)}）"
    return res


def fmt_num(x: Any, digits: int = 2) -> str:
    try:
        v = float(x)
        return f"{v:,.{digits}f}" if abs(v) < 1000 else f"{v:,.0f}"
    except Exception:
        return "-"


def metric(label: str, value: str, note: str = "") -> None:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-note'>{note}</div></div>", unsafe_allow_html=True)


def badge(text: str, kind: str = "gold") -> str:
    return f"<span class='badge badge-{kind}'>{text}</span>"


def plot_technical(prices: pd.DataFrame) -> go.Figure:
    df = prices.copy()
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.035,
        row_heights=[0.48, 0.16, 0.18, 0.18],
        subplot_titles=("日 K 線（含布林通道 / 均線）", "成交量", "RSI / KD", "MACD"),
    )
    inc, dec = "#c76a6a", "#7b9e89"
    fig.add_trace(go.Candlestick(x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], increasing_line_color=inc, decreasing_line_color=dec, name="K線"), row=1, col=1)
    for col, name, color in [("ma5", "MA5", "#cba365"), ("ma20", "MA20", "#6d98ab"), ("ma60", "MA60", "#b0889f"), ("bb_upper", "BB上緣", "#bdb6aa"), ("bb_lower", "BB下緣", "#bdb6aa")]:
        if col in df:
            fig.add_trace(go.Scatter(x=df["date"], y=df[col], mode="lines", name=name, line=dict(color=color, width=1.4, dash="dot" if "BB" in name else None)), row=1, col=1)
    colors = [inc if bool(v) else dec for v in df["is_up"]]
    fig.add_trace(go.Bar(x=df["date"], y=df["volume"] / 1000, name="成交量(千張)", marker_color=colors), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["rsi"], mode="lines", name="RSI", line=dict(color="#cba365", width=1.6)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["k"], mode="lines", name="K", line=dict(color="#6d98ab", width=1.3)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["d"], mode="lines", name="D", line=dict(color="#b0889f", width=1.3)), row=3, col=1)
    fig.add_hline(y=80, line_dash="dash", line_color="#d8bcbc", row=3, col=1)
    fig.add_hline(y=20, line_dash="dash", line_color="#bed2c5", row=3, col=1)
    hist_colors = [inc if float(v or 0) >= 0 else dec for v in df["macd_hist"]]
    fig.add_trace(go.Bar(x=df["date"], y=df["macd_hist"], name="MACD柱", marker_color=hist_colors), row=4, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["macd_dif"], mode="lines", name="DIF", line=dict(color="#6d98ab", width=1.5)), row=4, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["macd_dea"], mode="lines", name="DEA", line=dict(color="#cba365", width=1.5)), row=4, col=1)
    fig.update_layout(height=760, template="plotly_white", margin=dict(l=20, r=20, t=45, b=20), xaxis_rangeslider_visible=False, legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center"), paper_bgcolor="#fffdf8", plot_bgcolor="#fffdf8")
    fig.update_yaxes(showgrid=True, gridcolor="#efe8dd")
    fig.update_xaxes(showgrid=False)
    return fig


def plot_chips(chip10: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if chip10.empty:
        return fig
    fig.add_trace(go.Bar(x=chip10["date"], y=chip10["foreign"], name="外資", marker_color="#6d98ab"), secondary_y=False)
    fig.add_trace(go.Bar(x=chip10["date"], y=chip10["trust"], name="投信", marker_color="#c76a6a"), secondary_y=False)
    fig.add_trace(go.Bar(x=chip10["date"], y=chip10["dealer"], name="自營商", marker_color="#b0889f"), secondary_y=False)
    if "price" in chip10.columns:
        fig.add_trace(go.Scatter(x=chip10["date"], y=chip10["price"], name="股價", mode="lines+markers", line=dict(color="#cba365", width=2)), secondary_y=True)
    fig.update_layout(height=360, barmode="relative", template="plotly_white", margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="#fffdf8", plot_bgcolor="#fffdf8", legend=dict(orientation="h"))
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
    st.markdown(f"""
    <div class='hero'>
      <div class='hero-title'>📊 {APP_TITLE}</div>
      <div class='hero-sub'>輸入股票代號或中文名稱，串接 FinMind 股價 / 法人籌碼資料，並使用 Google Gemini 產出個股分析。資料僅供研究，不構成投資建議。</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='search-card'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2.4, 1, 1])
        with c1:
            q = st.text_input("股票代號或中文名稱", value=st.session_state.get("query", "2330"), placeholder="例如：2330、台積電、友達")
        with c2:
            theme = st.selectbox("介面風格", ["莫蘭迪", "專業黑（預留）"], index=0)
        with c3:
            st.write("")
            run = st.button("SYSTEM START / 分析", use_container_width=True, type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

    if run or "last_bundle" not in st.session_state or q != st.session_state.get("query"):
        st.session_state["query"] = q
        with st.spinner("抓取 FinMind 資料並計算技術指標..."):
            try:
                bundle = fetch_stock_bundle(q)
                chip10 = aggregate_chips(bundle.chips, bundle.prices)
                qs = score_and_summary(bundle, chip10)
                with st.spinner("Google Gemini 量化分析與新聞整理中..."):
                    ai = call_gemini(bundle, chip10, qs)
                st.session_state["last_bundle"] = bundle
                st.session_state["last_chips"] = chip10
                st.session_state["last_qs"] = qs
                st.session_state["last_ai"] = ai
                st.session_state["error"] = None
            except Exception as exc:
                st.session_state["error"] = str(exc)

    if st.session_state.get("error"):
        st.error(st.session_state["error"])
        st.info("若是 Token 問題，請到 Streamlit Secrets 設定 FINMIND_TOKENS 與 GOOGLE_API_KEYS。")
        return

    bundle: StockBundle = st.session_state.get("last_bundle")
    if bundle is None:
        return
    chip10: pd.DataFrame = st.session_state["last_chips"]
    qs: dict[str, Any] = st.session_state["last_qs"]
    ai: dict[str, Any] = st.session_state["last_ai"]
    latest = bundle.prices.iloc[-1]
    prev_close = float(latest["close"] - (latest.get("spread", 0) or 0)) if pd.notna(latest.get("spread")) else float(bundle.prices.iloc[-2]["close"])
    pct = (float(latest["close"]) - prev_close) / prev_close * 100 if prev_close else 0
    up = pct >= 0
    rev = latest_revenue(bundle.revenue)

    st.markdown(f"## {bundle.stock_name}（{bundle.stock_id}）AI 分析報告")
    st.caption(f"產業：{bundle.industry or '-'} ｜ 報告生成：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 整體狀態：{qs['status']}")

    m1, m2, m3 = st.columns(3)
    with m1:
        metric("即時收盤價", f"{float(latest['close']):g}", f"{'▲' if up else '▼'} {pct:+.2f}%")
    with m2:
        metric("成交量", f"{int(round(float(latest['volume']) / 1000)):,} 張", qs["volume_status"])
    with m3:
        metric("偏多分數", f"{qs['score']} / 100", ai.get("tag", {}).get("reason", ""))

    st.markdown("### 🚦警示燈號")
    kinds = ["green", "gold", "blue", "red"]
    st.markdown("".join(badge(r, kinds[i % len(kinds)]) for i, r in enumerate(qs["reasons"])), unsafe_allow_html=True)

    st.markdown("### 📈趨勢圖表（日 K 線）")
    st.plotly_chart(plot_technical(bundle.prices), use_container_width=True)

    st.markdown("### 📈技術面總覽")
    t1, t2, t3, t4 = st.columns(4)
    with t1: metric("趨勢方向", qs["trend"])
    with t2: metric("RSI(14)", fmt_num(latest.get("rsi")))
    with t3: metric("MACD 狀態", qs["macd_status"])
    with t4: metric("量能變化", qs["volume_status"])
    t5, t6, t7 = st.columns(3)
    with t5: metric("MA5", fmt_num(latest.get("ma5")))
    with t6: metric("MA20", fmt_num(latest.get("ma20")))
    with t7: metric("MA60", fmt_num(latest.get("ma60")))

    st.markdown("### 👥籌碼面動向")
    c1, c2, c3, c4 = st.columns(4)
    foreign = int(chip10.iloc[-1]["foreign"]) if not chip10.empty else 0
    trust = int(chip10.iloc[-1]["trust"]) if not chip10.empty else 0
    dealer = int(chip10.iloc[-1]["dealer"]) if not chip10.empty else 0
    total = int(chip10.iloc[-1]["total"]) if not chip10.empty else 0
    with c1: metric("外資(千張)", f"{foreign:+,}")
    with c2: metric("投信(千張)", f"{trust:+,}")
    with c3: metric("自營商(千張)", f"{dealer:+,}")
    with c4: metric("合計(千張)", f"{total:+,}")
    st.plotly_chart(plot_chips(chip10), use_container_width=True)

    st.markdown("### 📊基本面")
    b1, b2, b3 = st.columns(3)
    with b1: metric("最新月營收", rev["revenue"], f"營收月份 {rev.get('period', '-')}")
    with b2: metric("YoY 年增率", rev["yoy"])
    with b3: metric("MoM 月增率", rev["mom"])

    st.markdown("### 🎯關鍵價位")
    l1, l2, l3, l4 = st.columns(4)
    levels = ai.get("levels", qs["levels"])
    with l1: metric("條件進場價", str(levels.get("entry", qs["levels"].get("entry"))))
    with l2: metric("壓力區", str(levels.get("pressure", qs["levels"].get("pressure"))))
    with l3: metric("支撐區", str(levels.get("support", qs["levels"].get("support"))))
    with l4: metric("停損參考", str(levels.get("stop", qs["levels"].get("stop"))))

    st.markdown("### ⭐整體結論")
    st.markdown(f"<div class='ai-box'>{ai.get('verdict','-')}</div>", unsafe_allow_html=True)

    st.markdown("### 🤖AI 智能解析")
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown("<div class='section'><div class='section-title'>技術面 / 籌碼面</div>", unsafe_allow_html=True)
        st.write(ai.get("techConclusion", "-"))
        st.write(ai.get("chipConclusion", "-"))
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='section'><div class='section-title'>短線操作建議</div>", unsafe_allow_html=True)
        for s in ai.get("suggestions", []):
            st.write(f"• {s}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_right:
        st.markdown("<div class='section'><div class='section-title'>可能路徑</div>", unsafe_allow_html=True)
        for p in ai.get("paths", []):
            st.write(f"**{p.get('type','')}**：{p.get('title','')}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='section'><div class='section-title'>評分</div>", unsafe_allow_html=True)
        ratings = ai.get("ratings", {})
        st.write(f"股價趨勢：{stars(ratings.get('trend', 3))}")
        st.write(f"技術面：{stars(ratings.get('tech', 3))}")
        st.write(f"籌碼面：{stars(ratings.get('chip', 3))}")
        st.write(f"操作難度：{stars(ratings.get('diff', 3))}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### ⚠️風險評估")
    st.markdown(f"<div class='warn-box'>{ai.get('warning','投資有風險，請審慎評估。')}</div>", unsafe_allow_html=True)

    st.markdown("### 📰近期重要新聞")
    news = ai.get("news", []) or []
    if news:
        ncols = st.columns(4)
        for i, item in enumerate(news[:4]):
            with ncols[i % 4]:
                st.markdown(f"<div class='section'><b>{item.get('title','')}</b><br><span class='small-muted'>{item.get('source','市場新聞')} ｜ {item.get('date','')}</span></div>", unsafe_allow_html=True)
    else:
        st.info("Gemini 未回傳新聞；若要啟用新聞，請確認 GOOGLE_API_KEYS 與模型支援搜尋工具。")

    with st.expander("原始資料 / 除錯"):
        st.write("價格資料")
        st.dataframe(bundle.prices.tail(20), use_container_width=True)
        st.write("籌碼資料")
        st.dataframe(chip10, use_container_width=True)
        st.write("月營收資料")
        st.dataframe(bundle.revenue.tail(12), use_container_width=True)

    st.caption(f"📊資料來源：FinMind ｜ 🤖AI：Google Gemini ｜ Build：{APP_BUILD} ｜ ⚠️本報告僅供研究參考，不構成投資建議。")


render_app()
