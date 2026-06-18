import streamlit as st
import requests
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import re

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="구독자 실시간 트래커",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.stApp { background: #f4f6fb; }

[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e6f0;
}

/* 최상단 큰 숫자 카드 */
.hero-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
    border-radius: 20px;
    padding: 2.2rem 2.4rem;
    color: white;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.hero-card::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(99,179,237,0.18) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7ecfff;
    margin-bottom: 0.4rem;
}
.hero-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.6rem;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.02em;
    color: #ffffff;
}
.hero-sub {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.55);
    margin-top: 0.5rem;
}

/* 델타 뱃지 */
.delta-positive {
    display: inline-block;
    background: rgba(72,199,142,0.18);
    color: #48c78e;
    border: 1px solid rgba(72,199,142,0.35);
    border-radius: 20px;
    padding: 0.18rem 0.8rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 0.6rem;
}
.delta-negative {
    display: inline-block;
    background: rgba(240,82,82,0.15);
    color: #f05252;
    border: 1px solid rgba(240,82,82,0.3);
    border-radius: 20px;
    padding: 0.18rem 0.8rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 0.6rem;
}
.delta-zero {
    display: inline-block;
    background: rgba(160,160,180,0.15);
    color: #9090b0;
    border: 1px solid rgba(160,160,180,0.3);
    border-radius: 20px;
    padding: 0.18rem 0.8rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 0.6rem;
}

/* 스탯 카드 */
.stat-card {
    background: #ffffff;
    border: 1px solid #e2e6f0;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stat-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #a0a8c0;
    margin-bottom: 0.35rem;
}
.stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    color: #1a1a2e;
    line-height: 1.1;
}
.stat-sub {
    font-size: 0.76rem;
    color: #a0a8c0;
    margin-top: 0.25rem;
}

/* 채널 헤더 */
.ch-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #ffffff;
    border: 1px solid #e2e6f0;
    border-radius: 14px;
    padding: 1rem 1.4rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.ch-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #1a1a2e;
}
.ch-meta {
    font-size: 0.8rem;
    color: #9090b0;
    margin-top: 0.2rem;
}

/* 섹션 타이틀 */
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #2a2a40;
    border-left: 3px solid #3b82f6;
    padding-left: 0.75rem;
    margin: 1.4rem 0 0.9rem 0;
}

/* 로그 테이블 */
.log-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 1rem;
    border-bottom: 1px solid #f0f2f8;
    font-size: 0.84rem;
    color: #3a3a5c;
}
.log-row:last-child { border-bottom: none; }
.log-time { color: #9090b0; font-size: 0.78rem; }

/* 정지 배너 */
.stopped-banner {
    background: #fff8e7;
    border: 1px solid #fcd34d;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    color: #92600a;
    font-size: 0.86rem;
    margin-bottom: 1rem;
    text-align: center;
}

/* 입력 */
[data-testid="stTextInput"] input {
    background: #ffffff !important;
    border: 1px solid #d0d6e8 !important;
    border-radius: 10px !important;
    color: #1a1a2e !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}

.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    padding: 0.5rem 1.4rem !important;
    width: 100% !important;
    transition: opacity 0.15s !important;
}

/* 인포 박스 */
.info-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    color: #1e40af;
    font-size: 0.82rem;
    line-height: 1.65;
    margin-bottom: 0.8rem;
}

hr { border-color: #e2e6f0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────────
for key, default in {
    "tracking": False,
    "records": [],          # [{ts, subs}]
    "channel_info": None,
    "baseline": None,
    "channel_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────
# 유틸 함수
# ─────────────────────────────────────────────
def fmt_num(n: int) -> str:
    if n >= 100_000_000:
        return f"{n/100_000_000:.2f}억"
    if n >= 10_000:
        return f"{n/10_000:.1f}만"
    return f"{n:,}"


def get_channel_id(api_key: str, query: str) -> str | None:
    query = query.strip()
    if query.startswith("UC") and len(query) == 24:
        return query

    handle = query.lstrip("@")
    r = requests.get("https://www.googleapis.com/youtube/v3/channels", params={
        "part": "id", "forHandle": handle, "key": api_key,
    }, timeout=8)
    if r.ok:
        items = r.json().get("items", [])
        if items:
            return items[0]["id"]

    r2 = requests.get("https://www.googleapis.com/youtube/v3/search", params={
        "part": "snippet", "q": query, "type": "channel",
        "maxResults": 1, "key": api_key,
    }, timeout=8)
    if r2.ok:
        items2 = r2.json().get("items", [])
        if items2:
            return items2[0]["snippet"]["channelId"]
    return None


def get_channel_info(api_key: str, channel_id: str) -> dict | None:
    r = requests.get("https://www.googleapis.com/youtube/v3/channels", params={
        "part": "snippet,statistics",
        "id": channel_id,
        "key": api_key,
    }, timeout=8)
    if not r.ok:
        return None
    items = r.json().get("items", [])
    return items[0] if items else None


def fetch_subscribers(api_key: str, channel_id: str) -> int | None:
    r = requests.get("https://www.googleapis.com/youtube/v3/channels", params={
        "part": "statistics",
        "id": channel_id,
        "key": api_key,
    }, timeout=8)
    if not r.ok:
        return None
    items = r.json().get("items", [])
    if not items:
        return None
    raw = items[0].get("statistics", {}).get("subscriberCount")
    return int(raw) if raw else None


def speed_label(per_hour: float) -> str:
    if per_hour >= 10_000:
        return "🚀 폭발적 증가"
    if per_hour >= 1_000:
        return "⚡ 매우 빠름"
    if per_hour >= 100:
        return "📈 빠름"
    if per_hour >= 10:
        return "➡️ 보통"
    if per_hour > 0:
        return "🐢 느림"
    if per_hour < 0:
        return "📉 감소 중"
    return "— 변동 없음"


def calc_stats(records: list) -> dict:
    if len(records) < 2:
        return {}
    df = pd.DataFrame(records)
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.sort_values("ts")

    delta_total = df["subs"].iloc[-1] - df["subs"].iloc[0]
    elapsed_sec = (df["ts"].iloc[-1] - df["ts"].iloc[0]).total_seconds()
    elapsed_min = max(elapsed_sec / 60, 1e-6)
    elapsed_hr  = max(elapsed_sec / 3600, 1e-6)

    per_min  = delta_total / elapsed_min
    per_hour = delta_total / elapsed_hr
    per_day  = per_hour * 24

    # 최대 단일 변화
    diffs = df["subs"].diff().dropna()
    max_jump = int(diffs.max()) if len(diffs) else 0

    return {
        "delta_total": delta_total,
        "per_min": per_min,
        "per_hour": per_hour,
        "per_day": per_day,
        "elapsed_min": elapsed_min,
        "max_jump": max_jump,
        "count": len(records),
    }


# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ 설정")
    st.markdown("---")

    api_key = st.text_input(
        "YouTube Data API v3 키",
        type="password",
        placeholder="AIzaSy...",
    )

    st.markdown("""
<div class="info-box">
🔑 <b>API 키 발급</b><br>
Google Cloud Console → YouTube Data API v3 활성화 → 사용자 인증 정보 → API 키 생성
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    channel_query = st.text_input(
        "채널명 또는 @핸들",
        placeholder="@MrBeast  /  긱블  /  UCxxxxxxxx",
    )

    interval = st.select_slider(
        "갱신 주기",
        options=[5, 10, 15, 30, 60, 120, 300],
        value=10,
        format_func=lambda x: f"{x}초" if x < 60 else f"{x//60}분",
    )

    col_s, col_e = st.columns(2)
    with col_s:
        start_btn = st.button("▶ 시작", type="primary")
    with col_e:
        stop_btn  = st.button("⏹ 정지")

    if st.button("🗑 기록 초기화"):
        st.session_state.records = []
        st.session_state.baseline = None
        st.session_state.channel_info = None
        st.session_state.channel_id = None
        st.rerun()

    st.markdown("---")
    st.markdown("""
<div class="info-box">
📌 <b>참고</b><br>
YouTube API는 구독자 수를 <b>약 1,000단위</b>로 반올림하여 제공합니다. 정확한 실시간 값이 아닌 근사치임을 감안해주세요.<br><br>
무료 할당량: 하루 <b>10,000 유닛</b><br>
(채널 조회 1회 = 1 유닛)
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 시작 버튼 처리
# ─────────────────────────────────────────────
if start_btn:
    if not api_key:
        st.sidebar.error("API 키를 입력해주세요.")
    elif not channel_query:
        st.sidebar.warning("채널명을 입력해주세요.")
    else:
        with st.spinner("채널 검색 중..."):
            cid = get_channel_id(api_key, channel_query)
        if not cid:
            st.sidebar.error(f"'{channel_query}' 채널을 찾을 수 없습니다.")
        else:
            info = get_channel_info(api_key, cid)
            if info:
                subs = int(info.get("statistics", {}).get("subscriberCount", 0))
                st.session_state.channel_id   = cid
                st.session_state.channel_info = info
                st.session_state.baseline     = subs
                st.session_state.records      = [{"ts": datetime.now().isoformat(), "subs": subs}]
                st.session_state.tracking     = True
            else:
                st.sidebar.error("채널 정보를 불러오지 못했습니다.")

if stop_btn:
    st.session_state.tracking = False


# ─────────────────────────────────────────────
# 메인 UI
# ─────────────────────────────────────────────
st.markdown('<p style="font-family:Space Grotesk,sans-serif;font-size:2rem;font-weight:700;color:#1a1a2e;margin-bottom:0">📡 구독자 실시간 트래커</p>', unsafe_allow_html=True)
st.markdown('<p style="color:#9090b0;font-size:0.9rem;margin-bottom:1.5rem">YouTube 채널 구독자 증감을 실시간으로 추적합니다</p>', unsafe_allow_html=True)

# 트래킹 중이 아닐 때 안내
if not st.session_state.tracking and not st.session_state.records:
    st.markdown("""
<div style="background:#ffffff;border:1px solid #e2e6f0;border-radius:16px;padding:3rem 2rem;text-align:center;color:#9090b0;box-shadow:0 1px 4px rgba(0,0,0,0.05)">
    <div style="font-size:3rem;margin-bottom:1rem">📺</div>
    <div style="font-family:Space Grotesk,sans-serif;font-size:1.2rem;font-weight:600;color:#3a3a5c;margin-bottom:0.5rem">
        사이드바에서 채널을 입력하고 시작하세요
    </div>
    <div style="font-size:0.86rem">
        채널명, @핸들, 채널 ID 모두 지원합니다
    </div>
</div>
""", unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
# 트래킹 중: API 호출 & 기록 추가
# ─────────────────────────────────────────────
if st.session_state.tracking and st.session_state.channel_id:
    current_subs = fetch_subscribers(api_key, st.session_state.channel_id)
    if current_subs is not None:
        last_ts = st.session_state.records[-1]["ts"] if st.session_state.records else None
        now_iso = datetime.now().isoformat()
        # 마지막 기록으로부터 interval 이상 지났을 때만 추가
        if last_ts is None or (datetime.now() - datetime.fromisoformat(last_ts)).total_seconds() >= interval:
            st.session_state.records.append({"ts": now_iso, "subs": current_subs})


# ─────────────────────────────────────────────
# 데이터 준비
# ─────────────────────────────────────────────
records = st.session_state.records
info    = st.session_state.channel_info
cid     = st.session_state.channel_id

if not records:
    st.info("데이터를 수집 중입니다...")
    st.stop()

latest_subs = records[-1]["subs"]
baseline    = st.session_state.baseline or latest_subs
delta_from_start = latest_subs - baseline
stats = calc_stats(records)

snippet = info.get("snippet", {}) if info else {}
ch_title = snippet.get("title", "채널")
ch_thumb = snippet.get("thumbnails", {}).get("default", {}).get("url", "")
ch_desc  = snippet.get("description", "")[:80]
started_at = datetime.fromisoformat(records[0]["ts"]).strftime("%H:%M:%S")

# ─────────────────────────────────────────────
# 채널 헤더
# ─────────────────────────────────────────────
thumb_html = f'<img src="{ch_thumb}" style="width:44px;height:44px;border-radius:50%;border:2px solid #e2e6f0"/>' if ch_thumb else "📺"
tracking_badge = (
    '<span style="background:#dcfce7;color:#16a34a;border:1px solid #bbf7d0;border-radius:20px;padding:0.15rem 0.65rem;font-size:0.74rem;font-weight:600;margin-left:0.5rem">● 추적 중</span>'
    if st.session_state.tracking else
    '<span style="background:#fef9c3;color:#92600a;border:1px solid #fde68a;border-radius:20px;padding:0.15rem 0.65rem;font-size:0.74rem;font-weight:600;margin-left:0.5rem">⏸ 정지됨</span>'
)
st.markdown(f"""
<div class="ch-header">
    {thumb_html}
    <div style="flex:1">
        <div class="ch-title">{ch_title} {tracking_badge}</div>
        <div class="ch-meta">{ch_desc or cid} &nbsp;|&nbsp; 추적 시작: {started_at} &nbsp;|&nbsp; 측정 횟수: {len(records)}회</div>
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.tracking and records:
    st.markdown('<div class="stopped-banner">⏸ 추적이 정지되었습니다. 사이드바에서 다시 시작할 수 있습니다.</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 히어로 카드 + 스탯 카드
# ─────────────────────────────────────────────
left_col, right_col = st.columns([5, 4], gap="medium")

with left_col:
    # 증감 뱃지
    if delta_from_start > 0:
        delta_html = f'<span class="delta-positive">▲ +{fmt_num(delta_from_start)} (추적 시작 이후)</span>'
    elif delta_from_start < 0:
        delta_html = f'<span class="delta-negative">▼ {fmt_num(delta_from_start)} (추적 시작 이후)</span>'
    else:
        delta_html = '<span class="delta-zero">— 변동 없음</span>'

    st.markdown(f"""
<div class="hero-card">
    <div class="hero-label">현재 구독자 수</div>
    <div class="hero-number">{latest_subs:,}</div>
    <div class="hero-sub">{fmt_num(latest_subs)} · 마지막 갱신 {datetime.fromisoformat(records[-1]["ts"]).strftime("%H:%M:%S")}</div>
    {delta_html}
</div>
""", unsafe_allow_html=True)

with right_col:
    if stats:
        ph = stats["per_hour"]
        pd_ = stats["per_day"]
        pm  = stats["per_min"]

        s1, s2 = st.columns(2)
        with s1:
            sign = "+" if ph >= 0 else ""
            st.markdown(f"""
<div class="stat-card">
    <div class="stat-label">시간당 증감</div>
    <div class="stat-value" style="color:{'#16a34a' if ph>0 else '#dc2626' if ph<0 else '#6b7280'}">{sign}{ph:+,.0f}</div>
    <div class="stat-sub">{speed_label(ph)}</div>
</div>""", unsafe_allow_html=True)

        with s2:
            sign2 = "+" if pd_ >= 0 else ""
            st.markdown(f"""
<div class="stat-card">
    <div class="stat-label">일 예상 증감</div>
    <div class="stat-value" style="color:{'#16a34a' if pd_>0 else '#dc2626' if pd_<0 else '#6b7280'}">{sign2}{pd_:+,.0f}</div>
    <div class="stat-sub">현재 속도 기준</div>
</div>""", unsafe_allow_html=True)

        s3, s4 = st.columns(2)
        with s3:
            elapsed_str = (
                f"{stats['elapsed_min']:.0f}분"
                if stats['elapsed_min'] < 60
                else f"{stats['elapsed_min']/60:.1f}시간"
            )
            st.markdown(f"""
<div class="stat-card">
    <div class="stat-label">추적 시간</div>
    <div class="stat-value">{elapsed_str}</div>
    <div class="stat-sub">{stats['count']}회 측정</div>
</div>""", unsafe_allow_html=True)

        with s4:
            st.markdown(f"""
<div class="stat-card">
    <div class="stat-label">분당 증감</div>
    <div class="stat-value">{pm:+.1f}</div>
    <div class="stat-sub">현재 속도 기준</div>
</div>""", unsafe_allow_html=True)
    else:
        st.info("데이터를 더 수집 중입니다... (2회 이상 측정 필요)")


# ─────────────────────────────────────────────
# 구독자 추이 차트
# ─────────────────────────────────────────────
if len(records) >= 2:
    st.markdown('<p class="section-title">구독자 추이</p>', unsafe_allow_html=True)

    df_chart = pd.DataFrame(records)
    df_chart["ts"] = pd.to_datetime(df_chart["ts"])
    df_chart["label"] = df_chart["ts"].dt.strftime("%H:%M:%S")

    fig = go.Figure()

    # 영역 채우기
    fig.add_trace(go.Scatter(
        x=df_chart["label"],
        y=df_chart["subs"],
        mode="lines+markers",
        name="구독자 수",
        line=dict(color="#3b82f6", width=2.5, shape="spline"),
        marker=dict(size=5, color="#3b82f6"),
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.08)",
        hovertemplate="<b>%{x}</b><br>구독자: %{y:,}<extra></extra>",
    ))

    # 기준선
    fig.add_hline(
        y=baseline,
        line_dash="dot",
        line_color="rgba(160,160,180,0.5)",
        annotation_text=f"시작: {baseline:,}",
        annotation_font=dict(color="#9090b0", size=11),
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(color="#3a3a5c", family="Noto Sans KR"),
        margin=dict(t=20, b=30, l=10, r=10),
        height=280,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=11),
            tickangle=-30,
        ),
        yaxis=dict(
            gridcolor="#f0f2f8",
            tickfont=dict(size=11),
            tickformat=",",
        ),
        hovermode="x unified",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# 증감 차트 (두 번째)
# ─────────────────────────────────────────────
if len(records) >= 3:
    st.markdown('<p class="section-title">측정 간 증감</p>', unsafe_allow_html=True)

    df2 = pd.DataFrame(records)
    df2["ts"] = pd.to_datetime(df2["ts"])
    df2["label"] = df2["ts"].dt.strftime("%H:%M:%S")
    df2["diff"] = df2["subs"].diff().fillna(0).astype(int)
    df2 = df2.iloc[1:]  # 첫 행 제거

    colors = ["#16a34a" if v >= 0 else "#dc2626" for v in df2["diff"]]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df2["label"],
        y=df2["diff"],
        marker_color=colors,
        hovertemplate="<b>%{x}</b><br>증감: %{y:+,}<extra></extra>",
    ))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(color="#3a3a5c", family="Noto Sans KR"),
        margin=dict(t=20, b=30, l=10, r=10),
        height=220,
        xaxis=dict(showgrid=False, tickfont=dict(size=11), tickangle=-30),
        yaxis=dict(gridcolor="#f0f2f8", tickfont=dict(size=11), tickformat="+,"),
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)


# ─────────────────────────────────────────────
# 측정 기록 로그
# ─────────────────────────────────────────────
if records:
    st.markdown('<p class="section-title">측정 기록</p>', unsafe_allow_html=True)

    log_rows = ""
    for i, rec in enumerate(reversed(records[-30:])):  # 최근 30개
        ts_str = datetime.fromisoformat(rec["ts"]).strftime("%H:%M:%S")
        subs   = rec["subs"]
        # 이전 값 대비 증감
        idx = len(records) - 1 - i
        if idx > 0:
            diff = subs - records[idx - 1]["subs"]
            if diff > 0:
                diff_html = f'<span style="color:#16a34a;font-weight:600">+{diff:,}</span>'
            elif diff < 0:
                diff_html = f'<span style="color:#dc2626;font-weight:600">{diff:,}</span>'
            else:
                diff_html = '<span style="color:#9090b0">±0</span>'
        else:
            diff_html = '<span style="color:#9090b0">기준</span>'

        log_rows += f"""
<div class="log-row">
    <span class="log-time">{ts_str}</span>
    <span style="font-family:Space Grotesk,sans-serif;font-weight:600;color:#1a1a2e">{subs:,}</span>
    <span>{diff_html}</span>
</div>"""

    st.markdown(f"""
<div style="background:#ffffff;border:1px solid #e2e6f0;border-radius:14px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.04)">
    <div style="display:flex;justify-content:space-between;padding:0.6rem 1rem;background:#f8faff;border-bottom:1px solid #e2e6f0;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;color:#9090b0">
        <span>시각</span><span>구독자 수</span><span>증감</span>
    </div>
    {log_rows}
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 자동 새로고침 (추적 중일 때만)
# ─────────────────────────────────────────────
if st.session_state.tracking:
    time.sleep(interval)
    st.rerun()
