import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from datetime import datetime, timedelta
import time

# ── 페이지 설정 ────────────────────────────────────────────────
st.set_page_config(
    page_title="유튜브 수익 분석기",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 커스텀 CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Space+Grotesk:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 배경 */
.stApp {
    background: #0f0f13;
    color: #e8e8f0;
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background: #17171f !important;
    border-right: 1px solid #2a2a38;
}

/* 헤더 */
.main-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ff4e4e 0%, #ff9c4e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
}

.sub-header {
    color: #7070a0;
    font-size: 0.95rem;
    margin-bottom: 2rem;
}

/* 메트릭 카드 */
.metric-card {
    background: #1c1c28;
    border: 1px solid #2a2a3e;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
}
.metric-label {
    color: #7070a0;
    font-size: 0.78rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #f0f0ff;
    line-height: 1.1;
}
.metric-sub {
    color: #7070a0;
    font-size: 0.78rem;
    margin-top: 0.3rem;
}
.metric-highlight {
    color: #ff7c4e;
}

/* 수익 범위 카드 */
.revenue-range {
    background: linear-gradient(135deg, #1e1530 0%, #1a2040 100%);
    border: 1px solid #3a2a5e;
    border-radius: 14px;
    padding: 1.6rem;
    text-align: center;
}
.revenue-range .range-label {
    color: #9070d0;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}
.revenue-range .range-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    line-height: 1;
}
.revenue-range .range-sub {
    color: #7070a0;
    font-size: 0.82rem;
    margin-top: 0.5rem;
}

/* 섹션 제목 */
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #c0c0e0;
    border-left: 3px solid #ff4e4e;
    padding-left: 0.8rem;
    margin: 1.6rem 0 1rem 0;
}

/* 채널 헤더 */
.channel-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #1c1c28;
    border: 1px solid #2a2a3e;
    border-radius: 14px;
    padding: 1.2rem 1.6rem;
    margin-bottom: 1.4rem;
}
.channel-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #f0f0ff;
}
.channel-desc {
    color: #7070a0;
    font-size: 0.84rem;
    margin-top: 0.2rem;
    line-height: 1.5;
}

/* 테이블 */
.video-table {
    background: #1c1c28;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #2a2a3e;
}

/* 알림 박스 */
.info-box {
    background: #1a2230;
    border: 1px solid #2a4060;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    color: #a0c0e0;
    font-size: 0.85rem;
    line-height: 1.6;
    margin-bottom: 1rem;
}

/* 입력 필드 스타일 */
[data-testid="stTextInput"] input {
    background: #1c1c28 !important;
    border: 1px solid #3a3a50 !important;
    border-radius: 10px !important;
    color: #f0f0ff !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 0.9rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #ff4e4e !important;
    box-shadow: 0 0 0 3px rgba(255, 78, 78, 0.15) !important;
}

/* 버튼 */
.stButton > button {
    background: linear-gradient(135deg, #ff4e4e, #ff7c4e) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 1.6rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
}

/* 구분선 */
hr {
    border-color: #2a2a3e !important;
}

/* Plotly 차트 배경 */
.js-plotly-plot {
    border-radius: 12px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


# ── 상수: CPM 기준값 (USD) ────────────────────────────────────
# 유튜브 평균 RPM(Revenue Per Mille) 범위
RPM_RANGES = {
    "education":     {"low": 3.0, "mid": 6.0, "high": 12.0},
    "finance":       {"low": 5.0, "mid": 10.0, "high": 20.0},
    "tech":          {"low": 3.5, "mid": 7.0, "high": 14.0},
    "gaming":        {"low": 1.5, "mid": 3.0, "high": 6.0},
    "entertainment": {"low": 1.0, "mid": 2.5, "high": 5.0},
    "lifestyle":     {"low": 1.5, "mid": 3.5, "high": 7.0},
    "news":          {"low": 2.0, "mid": 4.0, "high": 8.0},
    "default":       {"low": 1.5, "mid": 3.5, "high": 7.0},
}

USD_TO_KRW = 1380  # 환율 (대략)


# ── 유틸 함수 ────────────────────────────────────────────────
def fmt_number(n: int) -> str:
    if n >= 100_000_000:
        return f"{n/100_000_000:.1f}억"
    if n >= 10_000:
        return f"{n/10_000:.1f}만"
    return f"{n:,}"


def fmt_krw(usd: float) -> str:
    krw = usd * USD_TO_KRW
    if krw >= 100_000_000:
        return f"₩{krw/100_000_000:.1f}억"
    if krw >= 10_000:
        return f"₩{krw/10_000:.0f}만"
    return f"₩{krw:,.0f}"


def parse_duration(iso: str) -> int:
    """ISO 8601 duration → seconds"""
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso)
    if not m:
        return 0
    h, mn, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mn * 60 + s


def get_channel_id(api_key: str, query: str) -> str | None:
    """채널명 또는 @handle → channel_id"""
    # @handle 처리
    handle = query.strip().lstrip("@")

    # 직접 채널 ID인지 확인
    if query.startswith("UC") and len(query) == 24:
        return query

    # forHandle 검색 (신형 핸들)
    url = "https://www.googleapis.com/youtube/v3/channels"
    r = requests.get(url, params={
        "part": "id",
        "forHandle": handle,
        "key": api_key,
    }, timeout=10)
    if r.ok:
        items = r.json().get("items", [])
        if items:
            return items[0]["id"]

    # search API로 폴백
    url2 = "https://www.googleapis.com/youtube/v3/search"
    r2 = requests.get(url2, params={
        "part": "snippet",
        "q": query,
        "type": "channel",
        "maxResults": 1,
        "key": api_key,
    }, timeout=10)
    if r2.ok:
        items2 = r2.json().get("items", [])
        if items2:
            return items2[0]["snippet"]["channelId"]

    return None


def get_channel_info(api_key: str, channel_id: str) -> dict | None:
    url = "https://www.googleapis.com/youtube/v3/channels"
    r = requests.get(url, params={
        "part": "snippet,statistics,brandingSettings,contentDetails",
        "id": channel_id,
        "key": api_key,
    }, timeout=10)
    if not r.ok:
        return None
    items = r.json().get("items", [])
    return items[0] if items else None


def get_recent_videos(api_key: str, playlist_id: str, max_results: int = 30) -> list[dict]:
    """uploads 재생목록에서 최신 영상 가져오기"""
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    video_ids = []
    page_token = None

    while len(video_ids) < max_results:
        params = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": min(50, max_results - len(video_ids)),
            "key": api_key,
        }
        if page_token:
            params["pageToken"] = page_token
        r = requests.get(url, params=params, timeout=10)
        if not r.ok:
            break
        data = r.json()
        video_ids += [i["contentDetails"]["videoId"] for i in data.get("items", [])]
        page_token = data.get("nextPageToken")
        if not page_token:
            break

    if not video_ids:
        return []

    # 영상 상세 정보
    detail_url = "https://www.googleapis.com/youtube/v3/videos"
    videos = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        r = requests.get(detail_url, params={
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(chunk),
            "key": api_key,
        }, timeout=10)
        if r.ok:
            videos += r.json().get("items", [])

    return videos


def estimate_revenue(views: int, rpm: dict) -> dict:
    """조회수 → 수익 추정 (광고 적용률 ~45%)"""
    monetized_views = views * 0.45
    return {
        "low": monetized_views / 1000 * rpm["low"],
        "mid": monetized_views / 1000 * rpm["mid"],
        "high": monetized_views / 1000 * rpm["high"],
    }


def detect_category(channel_info: dict) -> str:
    """채널 카테고리 자동 감지"""
    desc = (
        channel_info.get("snippet", {}).get("description", "") +
        channel_info.get("snippet", {}).get("title", "")
    ).lower()
    kw_map = {
        "finance": ["finance", "invest", "stock", "crypto", "money", "trading", "경제", "투자", "주식", "코인"],
        "education": ["edu", "learn", "teach", "study", "course", "강의", "교육", "공부", "학습"],
        "tech": ["tech", "code", "program", "software", "dev", "ai", "기술", "코딩", "개발"],
        "gaming": ["game", "gaming", "play", "stream", "게임", "플레이"],
        "news": ["news", "뉴스", "시사", "정치"],
        "lifestyle": ["vlog", "life", "travel", "food", "라이프", "일상", "여행", "음식", "요리"],
    }
    for cat, kws in kw_map.items():
        if any(k in desc for k in kws):
            return cat
    return "default"


# ── 사이드바 ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ 설정")
    st.markdown("---")

    api_key = st.text_input(
        "YouTube Data API v3 키",
        type="password",
        placeholder="AIzaSy...",
        help="Google Cloud Console에서 발급받은 API 키를 입력하세요."
    )

    st.markdown("""
<div class="info-box">
🔑 <b>API 키 발급 방법</b><br>
1. <a href="https://console.cloud.google.com/" target="_blank" style="color:#7090d0">Google Cloud Console</a> 접속<br>
2. YouTube Data API v3 활성화<br>
3. 사용자 인증 정보 → API 키 생성
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    category_override = st.selectbox(
        "카테고리 수동 지정 (선택)",
        ["자동 감지", "교육", "금융/경제", "기술/IT", "게임", "엔터테인먼트", "라이프스타일", "뉴스/시사"],
        index=0,
    )
    cat_map = {
        "자동 감지": None, "교육": "education", "금융/경제": "finance",
        "기술/IT": "tech", "게임": "gaming", "엔터테인먼트": "entertainment",
        "라이프스타일": "lifestyle", "뉴스/시사": "news",
    }

    video_count = st.slider("분석할 최신 영상 수", 10, 50, 30, 5)

    st.markdown("---")
    st.markdown("""
<div class="info-box">
💡 <b>수익 추정 방식</b><br>
YouTube RPM(조회 1,000회당 수익) 기반 추정치입니다.<br>
실제 수익은 광고주, 시청자 지역, 시즌 등에 따라 크게 달라질 수 있습니다.
</div>
""", unsafe_allow_html=True)


# ── 메인 영역 ────────────────────────────────────────────────
st.markdown('<p class="main-header">📺 유튜브 수익 분석기</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">채널명 또는 @핸들을 입력하면 조회수 기반 수익을 추정합니다</p>', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    channel_query = st.text_input(
        "채널명 입력",
        placeholder="예: @MrBeast  /  긱블  /  UCxxxxxxxx",
        label_visibility="collapsed",
    )
with col_btn:
    analyze_btn = st.button("분석 시작 →")


# ── 분석 실행 ────────────────────────────────────────────────
if analyze_btn:
    if not api_key:
        st.error("⚠️ 사이드바에 YouTube Data API 키를 입력해주세요.")
        st.stop()
    if not channel_query:
        st.warning("채널명을 입력해주세요.")
        st.stop()

    with st.spinner("채널 정보를 가져오는 중..."):
        try:
            channel_id = get_channel_id(api_key, channel_query)
        except Exception as e:
            st.error(f"API 오류: {e}")
            st.stop()

    if not channel_id:
        st.error(f"'{channel_query}' 채널을 찾을 수 없습니다. 채널명이나 @핸들을 확인해주세요.")
        st.stop()

    with st.spinner("채널 통계 분석 중..."):
        channel_info = get_channel_info(api_key, channel_id)

    if not channel_info:
        st.error("채널 정보를 불러오지 못했습니다.")
        st.stop()

    snippet = channel_info.get("snippet", {})
    stats = channel_info.get("statistics", {})
    content_details = channel_info.get("contentDetails", {})

    title = snippet.get("title", "알 수 없음")
    description = snippet.get("description", "")[:120] + "..."
    thumbnail = snippet.get("thumbnails", {}).get("default", {}).get("url", "")
    created_at = snippet.get("publishedAt", "")[:10]
    subscribers = int(stats.get("subscriberCount", 0))
    total_views = int(stats.get("viewCount", 0))
    video_count_total = int(stats.get("videoCount", 0))
    uploads_id = content_details.get("relatedPlaylists", {}).get("uploads", "")

    # 카테고리 결정
    cat_key = cat_map[category_override] or detect_category(channel_info)
    rpm = RPM_RANGES.get(cat_key, RPM_RANGES["default"])

    # ── 채널 헤더 ──
    thumb_html = f'<img src="{thumbnail}" style="width:52px;height:52px;border-radius:50%;border:2px solid #3a3a50"/>' if thumbnail else "📺"
    st.markdown(f"""
<div class="channel-header">
    {thumb_html}
    <div>
        <div class="channel-name">{title}</div>
        <div class="channel-desc">{description}</div>
        <div style="color:#505070;font-size:0.76rem;margin-top:0.3rem">
            채널 개설: {created_at} &nbsp;|&nbsp; ID: {channel_id}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── 기본 통계 ──
    st.markdown('<p class="section-title">채널 기본 통계</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">구독자 수</div>
    <div class="metric-value">{fmt_number(subscribers)}</div>
    <div class="metric-sub">{subscribers:,}명</div>
</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">총 조회수</div>
    <div class="metric-value">{fmt_number(total_views)}</div>
    <div class="metric-sub">{total_views:,}회</div>
</div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">영상 수 / 평균 조회수</div>
    <div class="metric-value">{video_count_total:,}개</div>
    <div class="metric-sub">평균 {fmt_number(total_views // max(video_count_total,1))}회/영상</div>
</div>""", unsafe_allow_html=True)

    # ── 누적 수익 추정 ──
    st.markdown('<p class="section-title">누적 총 수익 추정</p>', unsafe_allow_html=True)
    total_rev = estimate_revenue(total_views, rpm)

    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f"""
<div class="revenue-range">
    <div class="range-label">🔽 보수적 추정</div>
    <div class="range-value" style="color:#a0a0ff">${total_rev['low']:,.0f}</div>
    <div class="range-sub">{fmt_krw(total_rev['low'])}</div>
</div>""", unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
<div class="revenue-range">
    <div class="range-label">⚖️ 중간 추정</div>
    <div class="range-value" style="color:#ff9c4e">${total_rev['mid']:,.0f}</div>
    <div class="range-sub">{fmt_krw(total_rev['mid'])}</div>
</div>""", unsafe_allow_html=True)
    with r3:
        st.markdown(f"""
<div class="revenue-range">
    <div class="range-label">🔼 낙관적 추정</div>
    <div class="range-value" style="color:#50e090">${total_rev['high']:,.0f}</div>
    <div class="range-sub">{fmt_krw(total_rev['high'])}</div>
</div>""", unsafe_allow_html=True)

    st.markdown(f"""
<div class="info-box" style="margin-top:0.8rem">
    📊 적용된 카테고리: <b>{cat_key}</b> &nbsp;|&nbsp;
    RPM 범위: <b>${rpm['low']} ~ ${rpm['high']}</b> (USD/1,000회)
</div>""", unsafe_allow_html=True)

    # ── 최신 영상 분석 ──
    if uploads_id:
        st.markdown('<p class="section-title">최신 영상 성과 분석</p>', unsafe_allow_html=True)

        with st.spinner(f"최신 {video_count}개 영상 불러오는 중..."):
            videos = get_recent_videos(api_key, uploads_id, max_results=video_count)

        if videos:
            rows = []
            for v in videos:
                vs = v.get("statistics", {})
                vc = v.get("contentDetails", {})
                vsnip = v.get("snippet", {})
                view_c = int(vs.get("viewCount", 0))
                rev = estimate_revenue(view_c, rpm)
                pub = vsnip.get("publishedAt", "")[:10]
                dur = parse_duration(vc.get("duration", "PT0S"))
                rows.append({
                    "제목": vsnip.get("title", "")[:50],
                    "게시일": pub,
                    "조회수": view_c,
                    "좋아요": int(vs.get("likeCount", 0)),
                    "댓글": int(vs.get("commentCount", 0)),
                    "길이(분)": round(dur / 60, 1),
                    "수익_low": rev["low"],
                    "수익_mid": rev["mid"],
                    "수익_high": rev["high"],
                })

            df = pd.DataFrame(rows)

            # 평균 지표
            avg_views = df["조회수"].mean()
            avg_rev_mid = df["수익_mid"].mean()
            monthly_rev_est = avg_rev_mid * 4  # 주 1회 업로드 가정

            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">최신 영상 평균 조회수</div>
    <div class="metric-value metric-highlight">{fmt_number(int(avg_views))}</div>
    <div class="metric-sub">최근 {len(df)}개 영상 기준</div>
</div>""", unsafe_allow_html=True)
            with mc2:
                st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">영상 1편당 예상 수익</div>
    <div class="metric-value metric-highlight">${avg_rev_mid:,.0f}</div>
    <div class="metric-sub">{fmt_krw(avg_rev_mid)} (중간 추정)</div>
</div>""", unsafe_allow_html=True)
            with mc3:
                st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">월 예상 수익 (주 1회 기준)</div>
    <div class="metric-value metric-highlight">${monthly_rev_est:,.0f}</div>
    <div class="metric-sub">{fmt_krw(monthly_rev_est)} (중간 추정)</div>
</div>""", unsafe_allow_html=True)

            # ── 차트 1: 영상별 조회수 ──
            fig1 = px.bar(
                df.head(20),
                x="제목", y="조회수",
                color="조회수",
                color_continuous_scale=["#3030a0", "#ff4e4e", "#ffaa4e"],
                title="",
            )
            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#13131c",
                font=dict(color="#c0c0e0", family="Noto Sans KR"),
                xaxis=dict(
                    tickangle=-40, tickfont=dict(size=10),
                    gridcolor="#2a2a3e", showgrid=False,
                ),
                yaxis=dict(gridcolor="#2a2a3e"),
                coloraxis_showscale=False,
                margin=dict(t=20, b=120),
                height=380,
            )
            fig1.update_traces(marker_line_width=0)

            # ── 차트 2: 영상별 수익 범위 ──
            fig2 = go.Figure()
            titles_short = [t[:20] + "…" if len(t) > 20 else t for t in df["제목"].head(20)]
            fig2.add_trace(go.Bar(
                x=titles_short, y=df["수익_high"].head(20),
                name="낙관", marker_color="rgba(80,224,144,0.35)",
            ))
            fig2.add_trace(go.Bar(
                x=titles_short, y=df["수익_mid"].head(20),
                name="중간", marker_color="rgba(255,156,78,0.85)",
            ))
            fig2.add_trace(go.Bar(
                x=titles_short, y=df["수익_low"].head(20),
                name="보수적", marker_color="rgba(160,160,255,0.85)",
            ))
            fig2.update_layout(
                barmode="overlay",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#13131c",
                font=dict(color="#c0c0e0", family="Noto Sans KR"),
                xaxis=dict(tickangle=-40, tickfont=dict(size=10), showgrid=False),
                yaxis=dict(gridcolor="#2a2a3e", title="수익 (USD)"),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(t=20, b=120),
                height=380,
            )

            tab1, tab2 = st.tabs(["📊 영상별 조회수", "💰 영상별 수익 추정"])
            with tab1:
                st.plotly_chart(fig1, use_container_width=True)
            with tab2:
                st.plotly_chart(fig2, use_container_width=True)

            # ── 상위 10 영상 테이블 ──
            st.markdown('<p class="section-title">조회수 TOP 10 영상</p>', unsafe_allow_html=True)
            top10 = df.nlargest(10, "조회수")[["제목", "게시일", "조회수", "좋아요", "댓글", "수익_mid"]].copy()
            top10.columns = ["제목", "게시일", "조회수", "👍 좋아요", "💬 댓글", "수익 추정 (USD)"]
            top10["조회수"] = top10["조회수"].apply(lambda x: f"{x:,}")
            top10["👍 좋아요"] = top10["👍 좋아요"].apply(lambda x: f"{x:,}")
            top10["💬 댓글"] = top10["💬 댓글"].apply(lambda x: f"{x:,}")
            top10["수익 추정 (USD)"] = top10["수익 추정 (USD)"].apply(lambda x: f"${x:,.0f}")
            st.dataframe(top10, use_container_width=True, hide_index=True)

        else:
            st.info("최신 영상 데이터를 불러올 수 없습니다.")


# ── 푸터 ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#404060;font-size:0.78rem;padding:0.5rem 0 1rem">
    ⚠️ 본 수익 추정은 공개 조회수 데이터와 평균 RPM 기반의 추정치입니다.
    실제 유튜브 수익은 다를 수 있으며 참고용으로만 활용하세요.
</div>
""", unsafe_allow_html=True)
