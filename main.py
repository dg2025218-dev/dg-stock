import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
 
# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 주식 비교 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ── CSS 스타일 ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');
 
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
 
    .stApp {
        background: #0a0e1a;
    }
 
    .main-header {
        background: linear-gradient(135deg, #0f1628 0%, #1a2340 50%, #0d1520 100%);
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
 
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(0, 212, 255, 0.08) 0%, transparent 70%);
        pointer-events: none;
    }
 
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d4ff, #7b68ee, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.25rem 0;
        letter-spacing: -0.5px;
    }
 
    .main-subtitle {
        color: #6b7fa3;
        font-size: 0.9rem;
        font-weight: 300;
        margin: 0;
    }
 
    .metric-card {
        background: #0f1628;
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.75rem;
        transition: border-color 0.2s;
    }
 
    .metric-card:hover {
        border-color: #00d4ff44;
    }
 
    .metric-label {
        font-size: 0.75rem;
        color: #6b7fa3;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.4rem;
    }
 
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.5rem;
        font-weight: 600;
        color: #e8eaf6;
    }
 
    .metric-delta-up {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #00e676;
    }
 
    .metric-delta-down {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #ff5252;
    }
 
    .section-header {
        font-size: 1rem;
        font-weight: 600;
        color: #a0b4d6;
        text-transform: uppercase;
        letter-spacing: 2px;
        padding: 0.5rem 0;
        border-bottom: 1px solid #1e3a5f;
        margin-bottom: 1rem;
    }
 
    .ticker-badge {
        display: inline-block;
        background: #1a2340;
        border: 1px solid #2a4070;
        border-radius: 6px;
        padding: 0.2rem 0.6rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #00d4ff;
        margin: 0.15rem;
    }
 
    .country-kr { border-color: #cd313a; color: #ff6b7a; }
    .country-us { border-color: #3c3b6e; color: #7b68ee; }
 
    .stSidebar > div {
        background: #080c18;
    }
 
    [data-testid="stSidebar"] {
        background: #080c18;
        border-right: 1px solid #1e3a5f;
    }
 
    div[data-testid="metric-container"] {
        background: #0f1628;
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 1rem;
    }
 
    .stSelectbox label, .stMultiSelect label, .stSlider label {
        color: #6b7fa3 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
 
    .leaderboard-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.7rem 1rem;
        background: #0f1628;
        border: 1px solid #1e3a5f;
        border-radius: 8px;
        margin-bottom: 0.4rem;
    }
 
    .rank-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #3a5080;
        width: 20px;
    }
 
    .stock-name-lb {
        flex: 1;
        margin-left: 0.75rem;
        font-size: 0.85rem;
        color: #c8d6f0;
    }
 
    .return-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        font-weight: 600;
    }
 
    .positive { color: #00e676; }
    .negative { color: #ff5252; }
    .neutral  { color: #6b7fa3; }
 
    /* 탭 스타일 */
    button[data-baseweb="tab"] {
        font-family: 'Noto Sans KR', sans-serif !important;
        font-size: 0.85rem !important;
        color: #6b7fa3 !important;
    }
 
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00d4ff !important;
    }
</style>
""", unsafe_allow_html=True)
 
# ── 데이터 ────────────────────────────────────────────────────────────────────
KOREAN_STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "현대차": "005380.KS",
    "POSCO홀딩스": "005490.KS",
    "카카오": "035720.KS",
    "NAVER": "035420.KS",
    "셀트리온": "068270.KS",
    "기아": "000270.KS",
    "삼성SDI": "006400.KS",
    "LG화학": "051910.KS",
    "KB금융": "105560.KS",
    "신한지주": "055550.KS",
    "하나금융지주": "086790.KS",
    "KT&G": "033780.KS",
    "크래프톤": "259960.KS",
    "두산에너빌리티": "034020.KS",
}
 
US_STOCKS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK-B",
    "JPMorgan Chase": "JPM",
    "Visa": "V",
    "Johnson & Johnson": "JNJ",
    "Exxon Mobil": "XOM",
    "UnitedHealth": "UNH",
    "Broadcom": "AVGO",
    "Netflix": "NFLX",
    "AMD": "AMD",
    "Palantir": "PLTR",
    "Coinbase": "COIN",
}
 
INDICES = {
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "다우존스": "^DJI",
}
 
PERIOD_OPTIONS = {
    "1주": "7d",
    "1개월": "1mo",
    "3개월": "3mo",
    "6개월": "6mo",
    "1년": "1y",
    "2년": "2y",
    "5년": "5y",
}
 
# ── 유틸 함수 ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_stock_data(ticker: str, period: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return pd.DataFrame()
 
@st.cache_data(ttl=300)
def fetch_current_price(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        return {
            "price": getattr(info, "last_price", None),
            "prev_close": getattr(info, "previous_close", None),
        }
    except Exception:
        return {"price": None, "prev_close": None}
 
def calc_return(df: pd.DataFrame) -> float | None:
    if df.empty or len(df) < 2:
        return None
    try:
        start = float(df["Close"].iloc[0])
        end = float(df["Close"].iloc[-1])
        if start == 0:
            return None
        return (end - start) / start * 100
    except Exception:
        return None
 
def color_class(val):
    if val is None:
        return "neutral"
    return "positive" if val >= 0 else "negative"
 
def fmt_return(val):
    if val is None:
        return "N/A"
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.2f}%"
 
# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-header">⚙ 설정</div>', unsafe_allow_html=True)
 
    period_label = st.selectbox(
        "기간 선택",
        list(PERIOD_OPTIONS.keys()),
        index=3,
    )
    period = PERIOD_OPTIONS[period_label]
 
    st.markdown('<div class="section-header" style="margin-top:1.5rem">🇰🇷 한국 주식</div>', unsafe_allow_html=True)
    selected_kr = st.multiselect(
        "한국 종목",
        list(KOREAN_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "현대차", "NAVER", "카카오"],
    )
 
    st.markdown('<div class="section-header" style="margin-top:1.5rem">🇺🇸 미국 주식</div>', unsafe_allow_html=True)
    selected_us = st.multiselect(
        "미국 종목",
        list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Microsoft", "Tesla", "Meta"],
    )
 
    st.markdown('<div class="section-header" style="margin-top:1.5rem">📊 지수</div>', unsafe_allow_html=True)
    selected_idx = st.multiselect(
        "비교 지수",
        list(INDICES.keys()),
        default=["KOSPI", "S&P 500"],
    )
 
    chart_type = st.radio(
        "차트 유형",
        ["정규화 수익률", "캔들스틱", "수익률 바 차트"],
        index=0,
    )
 
# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <p class="main-title">📈 글로벌 주식 비교 대시보드</p>
    <p class="main-subtitle">한국 · 미국 주요 종목 수익률 실시간 분석 &nbsp;·&nbsp; 기간: {period_label} &nbsp;·&nbsp; {datetime.now().strftime('%Y-%m-%d %H:%M')} 기준</p>
</div>
""", unsafe_allow_html=True)
 
# ── 선택 종목 합치기 ──────────────────────────────────────────────────────────
all_selected = []
for name in selected_kr:
    all_selected.append({"name": name, "ticker": KOREAN_STOCKS[name], "country": "KR"})
for name in selected_us:
    all_selected.append({"name": name, "ticker": US_STOCKS[name], "country": "US"})
for name in selected_idx:
    all_selected.append({"name": name, "ticker": INDICES[name], "country": "IDX"})
 
if not all_selected:
    st.warning("사이드바에서 종목을 선택해주세요.")
    st.stop()
 
# ── 데이터 로딩 ───────────────────────────────────────────────────────────────
with st.spinner("데이터를 불러오는 중…"):
    stock_data = {}
    returns = {}
    for s in all_selected:
        df = fetch_stock_data(s["ticker"], period)
        stock_data[s["name"]] = df
        returns[s["name"]] = calc_return(df)
 
# ── KPI 카드 (수익률 상위/하위) ───────────────────────────────────────────────
valid_returns = {k: v for k, v in returns.items() if v is not None}
if valid_returns:
    sorted_returns = sorted(valid_returns.items(), key=lambda x: x[1], reverse=True)
    best_name, best_val = sorted_returns[0]
    worst_name, worst_val = sorted_returns[-1]
    avg_val = np.mean(list(valid_returns.values()))
 
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="🏆 최고 수익률",
            value=best_name,
            delta=f"{best_val:+.2f}%",
        )
    with col2:
        st.metric(
            label="📉 최저 수익률",
            value=worst_name,
            delta=f"{worst_val:+.2f}%",
            delta_color="inverse",
        )
    with col3:
        st.metric(
            label="📊 평균 수익률",
            value=f"{avg_val:+.2f}%",
            delta=f"{len(valid_returns)}개 종목",
        )
    with col4:
        pos = sum(1 for v in valid_returns.values() if v >= 0)
        neg = len(valid_returns) - pos
        st.metric(
            label="🟢 상승 / 🔴 하락",
            value=f"{pos} / {neg}",
            delta=f"{period_label} 기준",
        )
 
st.markdown("<br>", unsafe_allow_html=True)
 
# ── 탭 ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 차트 분석", "🏅 수익률 랭킹", "📋 상세 데이터"])
 
# ━━━ TAB 1 : 차트 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    COLORS_KR  = ["#ff6b7a", "#ff9a3c", "#ffd166", "#ef476f", "#f78c6b", "#ff4d6d", "#c9184a", "#ff0054"]
    COLORS_US  = ["#7b68ee", "#00d4ff", "#00b4d8", "#90e0ef", "#48cae4", "#0096c7", "#0077b6", "#023e8a"]
    COLORS_IDX = ["#a0e7a0", "#69db7c", "#40c057"]
 
    def get_color(s):
        idx_kr = [x for x in all_selected if x["country"] == "KR"]
        idx_us = [x for x in all_selected if x["country"] == "US"]
        idx_ix = [x for x in all_selected if x["country"] == "IDX"]
        names_kr = [x["name"] for x in idx_kr]
        names_us = [x["name"] for x in idx_us]
        names_ix = [x["name"] for x in idx_ix]
        if s in names_kr:
            return COLORS_KR[names_kr.index(s) % len(COLORS_KR)]
        elif s in names_us:
            return COLORS_US[names_us.index(s) % len(COLORS_US)]
        elif s in names_ix:
            return COLORS_IDX[names_ix.index(s) % len(COLORS_IDX)]
        return "#aaaaaa"
 
    # ─ 정규화 수익률 차트 ─────────────────────────────────────────────────────
    if chart_type == "정규화 수익률":
        fig = go.Figure()
        for s in all_selected:
            df = stock_data[s["name"]]
            if df.empty:
                continue
            close = df["Close"].squeeze()
            normalized = (close / close.iloc[0] - 1) * 100
            fig.add_trace(go.Scatter(
                x=normalized.index,
                y=normalized.values,
                name=s["name"],
                line=dict(color=get_color(s["name"]), width=2),
                hovertemplate=f"<b>{s['name']}</b><br>날짜: %{{x|%Y-%m-%d}}<br>수익률: %{{y:.2f}}%<extra></extra>",
            ))
 
        fig.add_hline(y=0, line_dash="dash", line_color="#3a5080", line_width=1)
        fig.update_layout(
            plot_bgcolor="#080c18",
            paper_bgcolor="#0a0e1a",
            font=dict(family="Noto Sans KR", color="#a0b4d6"),
            xaxis=dict(
                gridcolor="#1e3a5f",
                tickformat="%m/%d",
                showgrid=True,
            ),
            yaxis=dict(
                gridcolor="#1e3a5f",
                ticksuffix="%",
                showgrid=True,
                zeroline=False,
            ),
            legend=dict(
                bgcolor="#0f1628",
                bordercolor="#1e3a5f",
                borderwidth=1,
                font=dict(size=11),
            ),
            hovermode="x unified",
            height=520,
            margin=dict(l=0, r=0, t=30, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)
 
    # ─ 캔들스틱 (단일 종목) ──────────────────────────────────────────────────
    elif chart_type == "캔들스틱":
        non_idx = [s for s in all_selected if s["country"] != "IDX"]
        if not non_idx:
            st.info("캔들스틱 차트는 개별 종목만 지원합니다.")
        else:
            candle_target = st.selectbox(
                "캔들스틱 종목 선택",
                [s["name"] for s in non_idx],
            )
            df = stock_data[candle_target]
            if df.empty:
                st.error(f"{candle_target} 데이터를 불러올 수 없습니다.")
            else:
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    row_heights=[0.75, 0.25],
                )
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df["Open"].squeeze(),
                    high=df["High"].squeeze(),
                    low=df["Low"].squeeze(),
                    close=df["Close"].squeeze(),
                    name=candle_target,
                    increasing=dict(line=dict(color="#00e676"), fillcolor="#00e67633"),
                    decreasing=dict(line=dict(color="#ff5252"), fillcolor="#ff525233"),
                ), row=1, col=1)
 
                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df["Volume"].squeeze(),
                    name="거래량",
                    marker_color=[
                        "#00e676" if c >= o else "#ff5252"
                        for c, o in zip(df["Close"].squeeze(), df["Open"].squeeze())
                    ],
                    opacity=0.6,
                ), row=2, col=1)
 
                # 이동평균선
                close = df["Close"].squeeze()
                for window, color, label in [(20, "#ffd166", "MA20"), (60, "#7b68ee", "MA60")]:
                    if len(close) >= window:
                        ma = close.rolling(window).mean()
                        fig.add_trace(go.Scatter(
                            x=df.index, y=ma,
                            name=label,
                            line=dict(color=color, width=1.5, dash="dot"),
                            hovertemplate=f"{label}: %{{y:.0f}}<extra></extra>",
                        ), row=1, col=1)
 
                fig.update_layout(
                    plot_bgcolor="#080c18",
                    paper_bgcolor="#0a0e1a",
                    font=dict(family="Noto Sans KR", color="#a0b4d6"),
                    xaxis=dict(gridcolor="#1e3a5f", rangeslider=dict(visible=False)),
                    xaxis2=dict(gridcolor="#1e3a5f"),
                    yaxis=dict(gridcolor="#1e3a5f"),
                    yaxis2=dict(gridcolor="#1e3a5f", title="거래량"),
                    legend=dict(bgcolor="#0f1628", bordercolor="#1e3a5f", borderwidth=1),
                    height=600,
                    margin=dict(l=0, r=0, t=30, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)
 
    # ─ 수익률 바 차트 ─────────────────────────────────────────────────────────
    else:
        sorted_items = sorted(
            [(s["name"], s["country"], returns[s["name"]]) for s in all_selected if returns[s["name"]] is not None],
            key=lambda x: x[1] if x[1] is not None else 0,
            reverse=True,
        )
        names = [x[0] for x in sorted_items]
        vals  = [x[1] for x in sorted_items]
        colors = [
            "#00e676" if v >= 0 else "#ff5252" for v in vals
        ]
        fig = go.Figure(go.Bar(
            x=names,
            y=vals,
            marker_color=colors,
            text=[fmt_return(v) for v in vals],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>수익률: %{y:.2f}%<extra></extra>",
        ))
        fig.add_hline(y=0, line_color="#3a5080", line_width=1)
        fig.update_layout(
            plot_bgcolor="#080c18",
            paper_bgcolor="#0a0e1a",
            font=dict(family="Noto Sans KR", color="#a0b4d6"),
            xaxis=dict(gridcolor="#1e3a5f"),
            yaxis=dict(gridcolor="#1e3a5f", ticksuffix="%"),
            height=480,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
 
    # ─ 산점도: 수익률 vs 변동성 ───────────────────────────────────────────────
    st.markdown('<div class="section-header" style="margin-top:1rem">리스크-수익률 산점도</div>', unsafe_allow_html=True)
    scatter_data = []
    for s in all_selected:
        df = stock_data[s["name"]]
        if df.empty or len(df) < 5:
            continue
        close = df["Close"].squeeze()
        ret = returns[s["name"]]
        vol = float(close.pct_change().dropna().std() * np.sqrt(252) * 100)
        scatter_data.append({
            "name": s["name"],
            "country": "🇰🇷 한국" if s["country"] == "KR" else ("🇺🇸 미국" if s["country"] == "US" else "📊 지수"),
            "return": ret,
            "volatility": vol,
        })
 
    if scatter_data:
        sdf = pd.DataFrame(scatter_data)
        fig2 = px.scatter(
            sdf,
            x="volatility",
            y="return",
            text="name",
            color="country",
            color_discrete_map={
                "🇰🇷 한국": "#ff6b7a",
                "🇺🇸 미국": "#7b68ee",
                "📊 지수": "#00e676",
            },
            labels={"volatility": "연환산 변동성 (%)", "return": f"수익률 (%, {period_label})"},
            height=400,
        )
        fig2.update_traces(textposition="top center", marker=dict(size=10))
        fig2.add_hline(y=0, line_dash="dash", line_color="#3a5080")
        fig2.update_layout(
            plot_bgcolor="#080c18",
            paper_bgcolor="#0a0e1a",
            font=dict(family="Noto Sans KR", color="#a0b4d6"),
            xaxis=dict(gridcolor="#1e3a5f"),
            yaxis=dict(gridcolor="#1e3a5f", ticksuffix="%"),
            legend=dict(bgcolor="#0f1628", bordercolor="#1e3a5f", borderwidth=1, title=""),
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)
 
# ━━━ TAB 2 : 랭킹 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    col_kr, col_us = st.columns(2)
 
    def render_leaderboard(title, items):
        st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
        ranked = sorted(
            [(s["name"], returns[s["name"]]) for s in items if returns[s["name"]] is not None],
            key=lambda x: x[1],
            reverse=True,
        )
        for i, (name, val) in enumerate(ranked, 1):
            medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else f"  {i}"))
            bar_width = min(abs(val) / max(abs(v) for _, v in ranked) * 80, 80) if ranked else 0
            bar_color = "#00e676" if val >= 0 else "#ff5252"
            st.markdown(f"""
            <div class="leaderboard-row">
                <span class="rank-num">{medal}</span>
                <span class="stock-name-lb">{name}</span>
                <div style="flex:1; padding: 0 1rem;">
                    <div style="height:4px; background:{bar_color}33; border-radius:2px;">
                        <div style="height:4px; width:{bar_width}%; background:{bar_color}; border-radius:2px;"></div>
                    </div>
                </div>
                <span class="return-val {'positive' if val >= 0 else 'negative'}">{fmt_return(val)}</span>
            </div>
            """, unsafe_allow_html=True)
 
    with col_kr:
        kr_stocks = [s for s in all_selected if s["country"] == "KR"]
        render_leaderboard("🇰🇷 한국 종목 수익률 랭킹", kr_stocks)
 
    with col_us:
        us_stocks = [s for s in all_selected if s["country"] == "US"]
        render_leaderboard("🇺🇸 미국 종목 수익률 랭킹", us_stocks)
 
    if selected_idx:
        st.markdown('<div class="section-header" style="margin-top:1rem">📊 주요 지수</div>', unsafe_allow_html=True)
        idx_stocks = [s for s in all_selected if s["country"] == "IDX"]
        cols = st.columns(len(idx_stocks))
        for col, s in zip(cols, idx_stocks):
            val = returns[s["name"]]
            with col:
                st.metric(
                    label=s["name"],
                    value=fmt_return(val),
                    delta=f"{'상승' if val and val >= 0 else '하락'} ({period_label})",
                    delta_color="normal" if (val and val >= 0) else "inverse",
                )
 
    # ─ 히트맵 ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header" style="margin-top:1rem">수익률 히트맵</div>', unsafe_allow_html=True)
    hm_names = [s["name"] for s in all_selected if returns[s["name"]] is not None]
    hm_vals  = [returns[n] for n in hm_names]
 
    if hm_names:
        n = len(hm_names)
        cols_n = min(n, 6)
        rows_n = (n + cols_n - 1) // cols_n
 
        z = []
        text_z = []
        y_labels = []
        for r in range(rows_n):
            row_z, row_t = [], []
            for c in range(cols_n):
                idx = r * cols_n + c
                if idx < n:
                    row_z.append(hm_vals[idx])
                    row_t.append(f"{hm_names[idx]}<br>{fmt_return(hm_vals[idx])}")
                else:
                    row_z.append(None)
                    row_t.append("")
            z.append(row_z)
            text_z.append(row_t)
            y_labels.append(f"그룹{r+1}")
 
        fig_hm = go.Figure(go.Heatmap(
            z=z,
            text=text_z,
            texttemplate="%{text}",
            textfont=dict(size=11, family="Noto Sans KR"),
            colorscale=[
                [0.0,  "#ff2244"],
                [0.35, "#992233"],
                [0.5,  "#1a2340"],
                [0.65, "#226633"],
                [1.0,  "#00e676"],
            ],
            showscale=True,
            colorbar=dict(
                ticksuffix="%",
                bgcolor="#0f1628",
                bordercolor="#1e3a5f",
            ),
            zmid=0,
        ))
        fig_hm.update_layout(
            plot_bgcolor="#080c18",
            paper_bgcolor="#0a0e1a",
            font=dict(family="Noto Sans KR", color="#a0b4d6"),
            xaxis=dict(showticklabels=False, showgrid=False),
            yaxis=dict(showticklabels=False, showgrid=False),
            height=max(200, rows_n * 90),
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_hm, use_container_width=True)
 
# ━━━ TAB 3 : 상세 데이터 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    table_rows = []
    for s in all_selected:
        df = stock_data[s["name"]]
        if df.empty:
            continue
        close = df["Close"].squeeze()
        ret   = returns[s["name"]]
        high  = float(close.max())
        low   = float(close.min())
        vol   = float(close.pct_change().dropna().std() * np.sqrt(252) * 100)
        last  = float(close.iloc[-1])
        table_rows.append({
            "종목": s["name"],
            "국가": "🇰🇷 한국" if s["country"] == "KR" else ("🇺🇸 미국" if s["country"] == "US" else "📊 지수"),
            "티커": s["ticker"],
            f"수익률({period_label})": f"{ret:+.2f}%" if ret is not None else "N/A",
            "현재가": f"{last:,.2f}",
            "기간 최고": f"{high:,.2f}",
            "기간 최저": f"{low:,.2f}",
            "연환산 변동성": f"{vol:.1f}%",
            "데이터 수": len(df),
        })
 
    if table_rows:
        tdf = pd.DataFrame(table_rows)
        st.dataframe(
            tdf,
            use_container_width=True,
            hide_index=True,
            column_config={
                f"수익률({period_label})": st.column_config.TextColumn(f"수익률({period_label})"),
            },
        )
 
        csv = tdf.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇ CSV 다운로드",
            data=csv,
            file_name=f"stock_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
 
# ── 푸터 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; color:#3a5080; font-size:0.75rem; margin-top:2rem; padding:1rem 0; border-top:1px solid #1e3a5f;'>
    데이터 제공: Yahoo Finance (yfinance) &nbsp;·&nbsp; 5분 캐시 적용 &nbsp;·&nbsp; 투자 참고용, 실제 투자 결정에 활용 시 주의
</div>
""", unsafe_allow_html=True)
