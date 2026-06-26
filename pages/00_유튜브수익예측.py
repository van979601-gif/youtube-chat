import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import json

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="유튜브 수익 분석기",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Space+Grotesk:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.stApp { background: #f7f8fc; color: #1a1a2e; }
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e4e6ef; }
[data-testid="stSidebar"] * { color: #2a2a40 !important; }
.main-header { font-family: 'Space Grotesk', sans-serif; font-size: 2.4rem; font-weight: 700; background: linear-gradient(135deg, #e8302a 0%, #ff7c2a 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.2rem; }
.sub-header { color: #7878a0; font-size: 0.95rem; margin-bottom: 2rem; }
.metric-card { background: #ffffff; border: 1px solid #e4e6ef; border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 0.8rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.metric-label { color: #9090b0; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem; }
.metric-value { font-family: 'Space Grotesk', sans-serif; font-size: 1.9rem; font-weight: 700; color: #1a1a2e; line-height: 1.1; }
.metric-sub { color: #9090b0; font-size: 0.78rem; margin-top: 0.3rem; }
.metric-highlight { color: #e8302a; }
.revenue-range { background: #ffffff; border: 1px solid #e4e6ef; border-radius: 14px; padding: 1.6rem; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.revenue-range .range-label { color: #9090b0; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }
.revenue-range .range-value { font-family: 'Space Grotesk', sans-serif; font-size: 2.4rem; font-weight: 700; line-height: 1; }
.revenue-range .range-sub { color: #9090b0; font-size: 0.82rem; margin-top: 0.5rem; }
.section-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 600; color: #2a2a40; border-left: 3px solid #e8302a; padding-left: 0.8rem; margin: 1.6rem 0 1rem 0; }
.channel-header { display: flex; align-items: center; gap: 1rem; background: #ffffff; border: 1px solid #e4e6ef; border-radius: 14px; padding: 1.2rem 1.6rem; margin-bottom: 1.4rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.channel-name { font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem; font-weight: 700; color: #1a1a2e; }
.channel-desc { color: #7878a0; font-size: 0.84rem; margin-top: 0.2rem; line-height: 1.5; }
.info-box { background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 10px; padding: 0.9rem 1.1rem; color: #4a5280; font-size: 0.85rem; line-height: 1.6; margin-bottom: 1rem; }
.warn-box { background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 0.85rem 1rem; color: #92600a; font-size: 0.82rem; line-height: 1.65; margin-bottom: 0.8rem; }
[data-testid="stTextInput"] input { background: #ffffff !important; border: 1px solid #d0d4e8 !important; border-radius: 10px !important; color: #1a1a2e !important; font-size: 0.95rem !important; padding: 0.6rem 0.9rem !important; }
[data-testid="stTextInput"] input:focus { border-color: #e8302a !important; box-shadow: 0 0 0 3px rgba(232,48,42,0.12) !important; }
.stButton > button { background: linear-gradient(135deg, #e8302a, #ff7c2a) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 700 !important; font-size: 0.95rem !important; padding: 0.55rem 1.6rem !important; width: 100% !important; transition: opacity 0.2s !important; }
.stButton > button:hover { opacity: 0.88 !important; }
hr { border-color: #e4e6ef !important; }
</style>
""", unsafe_allow_html=True)


# ── 상수 ─────────────────────────────────────────────────────
RPM_RANGES = {
    "education":     {"low": 3.0, "mid": 6.0,  "high": 12.0},
    "finance":       {"low": 5.0, "mid": 10.0, "high": 20.0},
    "tech":          {"low": 3.5, "mid": 7.0,  "high": 14.0},
    "gaming":        {"low": 1.5, "mid": 3.0,  "high": 6.0},
    "entertainment": {"low": 1.0, "mid": 2.5,  "high": 5.0},
    "lifestyle":     {"low": 1.5, "mid": 3.5,  "high": 7.0},
    "news":          {"low": 2.0, "mid": 4.0,  "high": 8.0},
    "default":       {"low": 1.5, "mid": 3.5,  "high": 7.0},
}
USD_TO_KRW = 1380

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
}


# ── 유틸 함수 ─────────────────────────────────────────────────
def fmt_number(n: int) -> str:
    if n >= 100_000_000: return f"{n/100_000_000:.1f}억"
    if n >= 10_000:      return f"{n/10_000:.1f}만"
    return f"{n:,}"

def fmt_krw(usd: float) -> str:
    krw = usd * USD_TO_KRW
    if krw >= 100_000_000: return f"₩{krw/100_000_000:.1f}억"
    if krw >= 10_000:      return f"₩{krw/10_000:.0f}만"
    return f"₩{krw:,.0f}"

def estimate_revenue(views: int, rpm: dict) -> dict:
    mv = views * 0.45
    return {"low": mv/1000*rpm["low"], "mid": mv/1000*rpm["mid"], "high": mv/1000*rpm["high"]}

def detect_category(title: str, desc: str) -> str:
    text = (title + " " + desc).lower()
    kw_map = {
        "finance":       ["finance","invest","stock","crypto","money","trading","경제","투자","주식","코인","재테크"],
        "education":     ["edu","learn","teach","study","course","강의","교육","공부","학습","튜토리얼"],
        "tech":          ["tech","code","program","software","dev","ai","기술","코딩","개발","it"],
        "gaming":        ["game","gaming","play","stream","게임","플레이","롤","배그","마인크래프트"],
        "news":          ["news","뉴스","시사","정치","사회"],
        "lifestyle":     ["vlog","life","travel","food","라이프","일상","여행","음식","요리","먹방"],
        "entertainment": ["comedy","funny","엔터","예능","개그","코미디","드라마"],
    }
    for cat, kws in kw_map.items():
        if any(k in text for k in kws):
            return cat
    return "default"


# ── 스크래핑 함수 (API 키 불필요) ────────────────────────────
def _resolve_url(query: str) -> str:
    q = query.strip()
    if q.startswith("http"):
        return q
    if q.startswith("@"):
        return f"https://www.youtube.com/{q}"
    return f"https://www.youtube.com/@{q}"

def _extract_initial_data(html: str) -> dict:
    """ytInitialData JSON 추출"""
    m = re.search(r"var ytInitialData\s*=\s*(\{.+?\});\s*(?:var|</script)", html, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    return {}

def _parse_count_text(text: str) -> int:
    """'104만', '1.2M', '1,040,000명' 등 → int"""
    if not text:
        return 0
    text = re.sub(r"[명의\s구독자]", "", text).replace(",", "")
    m = re.match(r"([\d.]+)\s*([만억KkMmBb]?)", text)
    if not m:
        return 0
    num  = float(m.group(1))
    unit = m.group(2).upper()
    return int(num * {"만":10_000,"억":100_000_000,"K":1_000,"M":1_000_000,"B":1_000_000_000}.get(unit, 1))

@st.cache_data(ttl=300, show_spinner=False)
def scrape_channel(query: str) -> dict | None:
    """채널 기본 정보 스크래핑 (구독자·총조회수·영상수·채널명·썸네일)"""
    url = _resolve_url(query)
    for suffix in ["", "/about", "/videos"]:
        try:
            r = requests.get(url + suffix, headers=HEADERS, timeout=12)
            if r.status_code != 200:
                continue
            html = r.text

            # ── 구독자 수 ──
            subs = 0
            m = re.search(r'"subscriberCountText"\s*:\s*\{"simpleText"\s*:\s*"([^"]+)"', html)
            if m:
                subs = _parse_count_text(m.group(1))
            if not subs:
                m2 = re.search(r'"subscriberCount"\s*:\s*"(\d+)"', html)
                if m2:
                    subs = int(m2.group(1))

            # ── 총 조회수 ──
            total_views = 0
            mv = re.search(r'"viewCountText"\s*:\s*\{"simpleText"\s*:\s*"([^"]+)"', html)
            if mv:
                total_views = _parse_count_text(re.sub(r"[^0-9만억KkMmBb.,]", "", mv.group(1)))
            if not total_views:
                mv2 = re.search(r'조회수\s*([\d,]+)', html)
                if mv2:
                    total_views = int(mv2.group(1).replace(",",""))

            # ── 영상 수 ──
            video_count = 0
            mvc = re.search(r'"videoCountText"\s*:\s*\{"runs"\s*:\s*\[\{"text"\s*:\s*"(\d+)"', html)
            if mvc:
                video_count = int(mvc.group(1))

            # ── 채널명 ──
            title = ""
            mt = re.search(r'"channelMetadataRenderer"\s*:\s*\{[^}]*?"title"\s*:\s*"([^"]+)"', html)
            if mt:
                title = mt.group(1)
            if not title:
                mt2 = re.search(r'<meta name="title" content="([^"]+)"', html)
                if mt2:
                    title = mt2.group(1)

            # ── 설명 ──
            desc = ""
            md = re.search(r'"description"\s*:\s*"([^"]{10,200})', html)
            if md:
                desc = md.group(1).replace("\\n", " ")

            # ── 썸네일 ──
            thumb = ""
            mth = re.search(r'"avatar"\s*:\s*\{"thumbnails"\s*:\s*\[\{"url"\s*:\s*"([^"]+)"', html)
            if mth:
                thumb = mth.group(1)
            if not thumb:
                mth2 = re.search(r'<link rel="image_src" href="([^"]+)"', html)
                if mth2:
                    thumb = mth2.group(1)

            # ── 개설일 ──
            created = ""
            mdate = re.search(r'"joinedDateText".*?"runs".*?"text"\s*:\s*"(\d{4})', html)
            if mdate:
                created = mdate.group(1)

            if not title and not subs:
                continue

            return {
                "title": title or query,
                "subs": subs,
                "total_views": total_views,
                "video_count": video_count,
                "desc": desc[:120],
                "thumb": thumb,
                "created": created,
                "url": url,
            }
        except Exception:
            continue
    return None


@st.cache_data(ttl=300, show_spinner=False)
def scrape_videos(channel_url: str, max_videos: int = 30) -> list[dict]:
    """채널 /videos 페이지에서 최신 영상 목록 스크래핑"""
    url = channel_url.rstrip("/") + "/videos"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            return []
        html = r.text

        # ytInitialData에서 영상 목록 추출
        data = _extract_initial_data(html)
        if not data:
            return []

        # 영상 아이템 탐색 (중첩 구조 순회)
        videos = []
        raw_str = json.dumps(data, ensure_ascii=False)

        # videoRenderer 패턴으로 영상 정보 추출
        pattern = re.compile(
            r'"videoId"\s*:\s*"([A-Za-z0-9_-]{11})".*?'
            r'"title"\s*:\s*\{"runs"\s*:\s*\[\{"text"\s*:\s*"([^"]+)".*?'
            r'"viewCountText"\s*:\s*\{"simpleText"\s*:\s*"([^"]+)"',
            re.DOTALL
        )

        seen = set()
        for m in pattern.finditer(raw_str):
            vid_id   = m.group(1)
            vid_title = m.group(2)
            view_text = m.group(3)
            if vid_id in seen:
                continue
            seen.add(vid_id)
            view_count = _parse_count_text(re.sub(r"[^0-9만억KkMmBb.,]", "", view_text))
            videos.append({
                "id":    vid_id,
                "title": vid_title,
                "views": view_count,
                "url":   f"https://www.youtube.com/watch?v={vid_id}",
            })
            if len(videos) >= max_videos:
                break

        # 날짜 패턴도 보완 시도
        date_pattern = re.compile(r'"publishedTimeText"\s*:\s*\{"simpleText"\s*:\s*"([^"]+)"')
        dates = date_pattern.findall(raw_str)
        for i, d in enumerate(dates[:len(videos)]):
            videos[i]["published"] = d

        return videos
    except Exception:
        return []


# ── 사이드바 ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ 설정")
    st.markdown("---")

    st.markdown("""
<div class="info-box">
✅ <b>API 키 불필요</b><br>
유튜브 채널 페이지를 직접 파싱합니다.<br>
별도 계정이나 API 키 없이 바로 사용 가능합니다.
</div>
""", unsafe_allow_html=True)

    category_override = st.selectbox(
        "카테고리 수동 지정 (선택)",
        ["자동 감지", "교육", "금융/경제", "기술/IT", "게임", "엔터테인먼트", "라이프스타일", "뉴스/시사"],
    )
    cat_map = {
        "자동 감지": None, "교육": "education", "금융/경제": "finance",
        "기술/IT": "tech", "게임": "gaming", "엔터테인먼트": "entertainment",
        "라이프스타일": "lifestyle", "뉴스/시사": "news",
    }

    video_count = st.slider("분석할 최신 영상 수", 10, 50, 30, 5)

    st.markdown("---")
    st.markdown("""
<div class="warn-box">
⚠️ <b>참고사항</b><br>
· 구독자·조회수는 YouTube 표시 기준 근사치입니다<br>
· 수익은 RPM 기반 추정치로 실제와 다를 수 있습니다<br>
· YouTube 페이지 구조 변경 시 일부 데이터가 누락될 수 있습니다
</div>
""", unsafe_allow_html=True)
    st.markdown("""
<div class="info-box">
💡 <b>수익 추정 방식</b><br>
광고 적용률 45% × RPM 범위로 계산합니다.<br>
카테고리별 RPM: 금융 $5~20 / 교육 $3~12 / 게임 $1.5~6
</div>
""", unsafe_allow_html=True)


# ── 메인 영역 ─────────────────────────────────────────────────
st.markdown('<p class="main-header">📺 유튜브 수익 분석기</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">채널명 또는 @핸들을 입력하면 조회수 기반 수익을 추정합니다 · API 키 불필요</p>', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    channel_query = st.text_input(
        "채널명 입력",
        placeholder="예: @MrBeast  /  긱블  /  https://youtube.com/@채널명",
        label_visibility="collapsed",
    )
with col_btn:
    analyze_btn = st.button("분석 시작 →")


# ── 분석 실행 ─────────────────────────────────────────────────
if analyze_btn:
    if not channel_query:
        st.warning("채널명을 입력해주세요.")
        st.stop()

    with st.spinner("채널 정보를 가져오는 중..."):
        channel = scrape_channel(channel_query)

    if not channel:
        st.error(
            f"'{channel_query}' 채널을 찾을 수 없습니다.\n\n"
            "· @핸들 형식으로 입력해보세요 (예: @채널명)\n"
            "· 채널 URL을 직접 붙여넣기 해보세요"
        )
        st.stop()

    title       = channel["title"]
    subs        = channel["subs"]
    total_views = channel["total_views"]
    video_cnt   = channel["video_count"]
    desc        = channel["desc"]
    thumb       = channel["thumb"]
    created     = channel["created"]
    ch_url      = channel["url"]

    # 카테고리 결정
    cat_key = cat_map[category_override] or detect_category(title, desc)
    rpm     = RPM_RANGES.get(cat_key, RPM_RANGES["default"])

    # ── 채널 헤더 ──────────────────────────────────────────────
    thumb_html = f'<img src="{thumb}" style="width:52px;height:52px;border-radius:50%;border:2px solid #e4e6ef"/>' if thumb else "📺"
    st.markdown(f"""
<div class="channel-header">
    {thumb_html}
    <div>
        <div class="channel-name">{title}</div>
        <div class="channel-desc">{desc or ch_url}</div>
        <div style="color:#9090b0;font-size:0.76rem;margin-top:0.3rem">
            {"개설: " + created + "년  |  " if created else ""}
            카테고리: {cat_key}  |  RPM ${ rpm['low']}~${rpm['high']}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── 기본 통계 ──────────────────────────────────────────────
    st.markdown('<p class="section-title">채널 기본 통계</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">구독자 수</div>
    <div class="metric-value">{fmt_number(subs) if subs else "비공개"}</div>
    <div class="metric-sub">{f"{subs:,}명" if subs else "채널에서 비공개 설정"}</div>
</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">총 조회수</div>
    <div class="metric-value">{fmt_number(total_views) if total_views else "—"}</div>
    <div class="metric-sub">{f"{total_views:,}회" if total_views else "데이터 없음"}</div>
</div>""", unsafe_allow_html=True)
    with c3:
        avg_v = total_views // max(video_cnt, 1) if video_cnt and total_views else 0
        st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">영상 수 / 평균 조회수</div>
    <div class="metric-value">{f"{video_cnt:,}개" if video_cnt else "—"}</div>
    <div class="metric-sub">{f"평균 {fmt_number(avg_v)}회/영상" if avg_v else "데이터 없음"}</div>
</div>""", unsafe_allow_html=True)

    # ── 누적 수익 추정 ─────────────────────────────────────────
    if total_views:
        st.markdown('<p class="section-title">누적 총 수익 추정</p>', unsafe_allow_html=True)
        total_rev = estimate_revenue(total_views, rpm)
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(f"""
<div class="revenue-range">
    <div class="range-label">🔽 보수적 추정</div>
    <div class="range-value" style="color:#6366f1">${total_rev['low']:,.0f}</div>
    <div class="range-sub">{fmt_krw(total_rev['low'])}</div>
</div>""", unsafe_allow_html=True)
        with r2:
            st.markdown(f"""
<div class="revenue-range">
    <div class="range-label">⚖️ 중간 추정</div>
    <div class="range-value" style="color:#f97316">${total_rev['mid']:,.0f}</div>
    <div class="range-sub">{fmt_krw(total_rev['mid'])}</div>
</div>""", unsafe_allow_html=True)
        with r3:
            st.markdown(f"""
<div class="revenue-range">
    <div class="range-label">🔼 낙관적 추정</div>
    <div class="range-value" style="color:#22c55e">${total_rev['high']:,.0f}</div>
    <div class="range-sub">{fmt_krw(total_rev['high'])}</div>
</div>""", unsafe_allow_html=True)

        st.markdown(f"""
<div class="info-box" style="margin-top:0.8rem">
    📊 적용 카테고리: <b>{cat_key}</b> &nbsp;|&nbsp; RPM 범위: <b>${rpm['low']} ~ ${rpm['high']}</b> (USD/1,000회) &nbsp;|&nbsp; 광고 적용률: <b>45%</b>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div class="warn-box">
⚠️ 총 조회수 데이터를 가져오지 못해 누적 수익 추정을 건너뜁니다.
</div>""", unsafe_allow_html=True)

    # ── 최신 영상 분석 ─────────────────────────────────────────
    st.markdown('<p class="section-title">최신 영상 성과 분석</p>', unsafe_allow_html=True)

    with st.spinner(f"최신 영상 {video_count}개 불러오는 중..."):
        videos = scrape_videos(ch_url, max_videos=video_count)

    if videos:
        rows = []
        for v in videos:
            rev = estimate_revenue(v["views"], rpm)
            rows.append({
                "제목":      v["title"][:50],
                "게시":      v.get("published", ""),
                "조회수":    v["views"],
                "수익_low":  rev["low"],
                "수익_mid":  rev["mid"],
                "수익_high": rev["high"],
                "url":       v["url"],
            })
        df = pd.DataFrame(rows)

        # 평균 지표
        avg_views    = df["조회수"].mean()
        avg_rev_mid  = df["수익_mid"].mean()
        monthly_est  = avg_rev_mid * 4

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
    <div class="metric-value metric-highlight">${monthly_est:,.0f}</div>
    <div class="metric-sub">{fmt_krw(monthly_est)} (중간 추정)</div>
</div>""", unsafe_allow_html=True)

        # ── 차트 ──────────────────────────────────────────────
        chart_df = df[df["조회수"] > 0].head(20).copy()

        if not chart_df.empty:
            fig1 = px.bar(
                chart_df, x="제목", y="조회수",
                color="조회수",
                color_continuous_scale=["#6366f1", "#e8302a", "#f97316"],
            )
            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f7f8fc",
                font=dict(color="#2a2a40", family="Noto Sans KR"),
                xaxis=dict(tickangle=-40, tickfont=dict(size=10), showgrid=False),
                yaxis=dict(gridcolor="#e4e6ef"),
                coloraxis_showscale=False,
                margin=dict(t=20, b=120), height=380,
            )
            fig1.update_traces(marker_line_width=0)

            titles_short = [t[:20]+"…" if len(t)>20 else t for t in chart_df["제목"]]
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=titles_short, y=chart_df["수익_high"], name="낙관",    marker_color="rgba(34,197,94,0.35)"))
            fig2.add_trace(go.Bar(x=titles_short, y=chart_df["수익_mid"],  name="중간",    marker_color="rgba(249,115,22,0.85)"))
            fig2.add_trace(go.Bar(x=titles_short, y=chart_df["수익_low"],  name="보수적",  marker_color="rgba(99,102,241,0.85)"))
            fig2.update_layout(
                barmode="overlay",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#f7f8fc",
                font=dict(color="#2a2a40", family="Noto Sans KR"),
                xaxis=dict(tickangle=-40, tickfont=dict(size=10), showgrid=False),
                yaxis=dict(gridcolor="#e4e6ef", title="수익 (USD)"),
                legend=dict(bgcolor="rgba(255,255,255,0.8)"),
                margin=dict(t=20, b=120), height=380,
            )

            tab1, tab2 = st.tabs(["📊 영상별 조회수", "💰 영상별 수익 추정"])
            with tab1:
                st.plotly_chart(fig1, use_container_width=True)
            with tab2:
                st.plotly_chart(fig2, use_container_width=True)

        # ── TOP 10 테이블 ──────────────────────────────────────
        st.markdown('<p class="section-title">조회수 TOP 10 영상</p>', unsafe_allow_html=True)
        top10 = df.nlargest(10, "조회수")[["제목","게시","조회수","수익_mid"]].copy()
        top10.columns = ["제목", "게시일", "조회수", "수익 추정 (USD)"]
        top10["조회수"]         = top10["조회수"].apply(lambda x: f"{x:,}")
        top10["수익 추정 (USD)"] = top10["수익 추정 (USD)"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(top10, use_container_width=True, hide_index=True)

    else:
        st.info("최신 영상 데이터를 불러오지 못했습니다. 채널 URL을 직접 입력해보세요.")


# ── 푸터 ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#9090b0;font-size:0.78rem;padding:0.5rem 0 1rem">
    ⚠️ 본 수익 추정은 공개 조회수 데이터와 평균 RPM 기반의 추정치입니다.
    실제 유튜브 수익은 다를 수 있으며 참고용으로만 활용하세요.
</div>
""", unsafe_allow_html=True)
