import streamlit as st
import requests
import time
import re
import json
import math
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

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
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e2e6f0; }
.hero-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
    border-radius: 20px; padding: 2.2rem 2.4rem; color: white;
    margin-bottom: 1.2rem; position: relative; overflow: hidden;
}
.hero-card::before {
    content:''; position:absolute; top:-40px; right:-40px;
    width:160px; height:160px;
    background:radial-gradient(circle,rgba(99,179,237,0.18) 0%,transparent 70%);
    border-radius:50%;
}
.hero-label { font-size:0.75rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:#7ecfff; margin-bottom:0.4rem; }
.hero-number { font-family:'Space Grotesk',sans-serif; font-size:3.8rem; font-weight:700; line-height:1; letter-spacing:-0.02em; color:#ffffff; font-variant-numeric:tabular-nums; }
.hero-sub { font-size:0.82rem; color:rgba(255,255,255,0.55); margin-top:0.5rem; }
.delta-positive { display:inline-block; background:rgba(72,199,142,0.18); color:#48c78e; border:1px solid rgba(72,199,142,0.35); border-radius:20px; padding:0.18rem 0.8rem; font-family:'Space Grotesk',sans-serif; font-size:0.9rem; font-weight:600; margin-top:0.6rem; }
.delta-negative { display:inline-block; background:rgba(240,82,82,0.15); color:#f05252; border:1px solid rgba(240,82,82,0.3); border-radius:20px; padding:0.18rem 0.8rem; font-family:'Space Grotesk',sans-serif; font-size:0.9rem; font-weight:600; margin-top:0.6rem; }
.delta-zero { display:inline-block; background:rgba(160,160,180,0.15); color:#9090b0; border:1px solid rgba(160,160,180,0.3); border-radius:20px; padding:0.18rem 0.8rem; font-family:'Space Grotesk',sans-serif; font-size:0.9rem; font-weight:600; margin-top:0.6rem; }
.stat-card { background:#ffffff; border:1px solid #e2e6f0; border-radius:14px; padding:1.1rem 1.3rem; margin-bottom:0.8rem; box-shadow:0 1px 3px rgba(0,0,0,0.05); }
.stat-label { font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; color:#a0a8c0; margin-bottom:0.35rem; }
.stat-value { font-family:'Space Grotesk',sans-serif; font-size:1.65rem; font-weight:700; color:#1a1a2e; line-height:1.1; }
.stat-sub { font-size:0.76rem; color:#a0a8c0; margin-top:0.25rem; }
.ch-header { display:flex; align-items:center; gap:1rem; background:#ffffff; border:1px solid #e2e6f0; border-radius:14px; padding:1rem 1.4rem; margin-bottom:1.2rem; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
.ch-title { font-family:'Space Grotesk',sans-serif; font-size:1.2rem; font-weight:700; color:#1a1a2e; }
.ch-meta { font-size:0.8rem; color:#9090b0; margin-top:0.2rem; }
.section-title { font-family:'Space Grotesk',sans-serif; font-size:1rem; font-weight:600; color:#2a2a40; border-left:3px solid #3b82f6; padding-left:0.75rem; margin:1.4rem 0 0.9rem 0; }
.log-row { display:flex; justify-content:space-between; align-items:center; padding:0.55rem 1rem; border-bottom:1px solid #f0f2f8; font-size:0.84rem; color:#3a3a5c; }
.log-row:last-child { border-bottom:none; }
.log-time { color:#9090b0; font-size:0.78rem; }
.stopped-banner { background:#fff8e7; border:1px solid #fcd34d; border-radius:10px; padding:0.7rem 1rem; color:#92600a; font-size:0.86rem; margin-bottom:1rem; text-align:center; }
[data-testid="stTextInput"] input { background:#ffffff !important; border:1px solid #d0d6e8 !important; border-radius:10px !important; color:#1a1a2e !important; }
[data-testid="stTextInput"] input:focus { border-color:#3b82f6 !important; box-shadow:0 0 0 3px rgba(59,130,246,0.12) !important; }
.stButton > button { border-radius:10px !important; font-weight:700 !important; font-size:0.92rem !important; padding:0.5rem 1.4rem !important; width:100% !important; transition:opacity 0.15s !important; }
.info-box { background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:0.85rem 1rem; color:#1e40af; font-size:0.82rem; line-height:1.65; margin-bottom:0.8rem; }
.warn-box { background:#fffbeb; border:1px solid #fde68a; border-radius:10px; padding:0.85rem 1rem; color:#92600a; font-size:0.82rem; line-height:1.65; margin-bottom:0.8rem; }
hr { border-color:#e2e6f0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────────
defaults = {
    "tracking":       False,
    "records":        [],      # 실제 API 스냅샷
    "smooth_records": [],      # 보간된 표시용 기록
    "channel_info":   None,
    "baseline":       None,
    "channel_url":    None,
    "per_sec":        0.0,     # 초당 예측 증가율
    "last_fetch_ts":  None,    # 마지막 실제 fetch 시각
    "last_fetch_val": None,    # 마지막 실제 fetch 값
    "start_ts":       None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
# 스크래핑 헬퍼
# ─────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
}

def _parse_sub(text: str) -> int:
    text = str(text).strip()
    # 정수 그대로
    if text.isdigit():
        return int(text)
    text = text.replace(",", "").replace(" ", "")
    # 한국어/영어 단위
    m = re.match(r"([\d.]+)\s*([만억KkMmBb]?)", text)
    if not m:
        return 0
    num  = float(m.group(1))
    unit = m.group(2).upper()
    mult = {"만":10_000,"억":100_000_000,"K":1_000,"M":1_000_000,"B":1_000_000_000}
    return int(num * mult.get(unit, 1))

def _resolve_url(query: str) -> str:
    q = query.strip()
    if q.startswith("http"):
        return q
    if q.startswith("@"):
        return f"https://www.youtube.com/{q}"
    return f"https://www.youtube.com/@{q}"

def _fetch_html(url: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        return r.text if r.status_code == 200 else None
    except Exception:
        return None

def scrape_channel(query: str) -> dict | None:
    """채널 기본 정보 + 정밀 구독자 수 스크래핑"""
    url = _resolve_url(query)

    for suffix in ["", "/about", "/featured"]:
        html = _fetch_html(url + suffix)
        if not html:
            continue

        # ── 구독자 (정밀: subscriberCount 숫자 우선) ──────────
        subs = 0
        # 패턴 A: 정수 그대로 ("subscriberCount":"29900000")
        ma = re.search(r'"subscriberCount"\s*:\s*"(\d+)"', html)
        if ma:
            subs = int(ma.group(1))

        # 패턴 B: subscriberCountText simpleText
        if not subs:
            mb = re.search(r'"subscriberCountText"\s*:\s*\{"simpleText"\s*:\s*"([^"]+)"', html)
            if mb:
                raw = mb.group(1)
                nm  = re.search(r"([\d,]+\.?\d*)\s*([만억KkMmBb]?)", raw)
                if nm:
                    subs = _parse_sub(nm.group(0))

        # 패턴 C: runs 배열
        if not subs:
            mc = re.search(r'"subscriberCountText".*?"text"\s*:\s*"([^"]+)"', html)
            if mc:
                subs = _parse_sub(mc.group(1))

        # 패턴 D: metadataRowContents
        if not subs:
            md = re.search(r'구독자\s*([\d.,]+\s*[만억KkMm]?)', html)
            if md:
                subs = _parse_sub(md.group(1))

        if not subs:
            continue

        # ── 채널명 ────────────────────────────────────────────
        title = ""
        mt = re.search(r'"channelMetadataRenderer"\s*:\s*\{[^}]*?"title"\s*:\s*"([^"]+)"', html)
        if mt:
            title = mt.group(1)
        if not title:
            mt2 = re.search(r'<meta name="title" content="([^"]+)"', html)
            if mt2:
                title = mt2.group(1)

        # ── 썸네일 ────────────────────────────────────────────
        thumb = ""
        mth = re.search(r'"avatar"\s*:\s*\{"thumbnails"\s*:\s*\[\{"url"\s*:\s*"([^"]+)"', html)
        if mth:
            thumb = mth.group(1)
        if not thumb:
            mth2 = re.search(r'<link rel="image_src" href="([^"]+)"', html)
            if mth2:
                thumb = mth2.group(1)

        # ── 설명 ─────────────────────────────────────────────
        desc = ""
        mde = re.search(r'"description"\s*:\s*"([^"]{10,160})', html)
        if mde:
            desc = mde.group(1).replace("\\n", " ")

        # ── 총 조회수 (증가율 계산용) ─────────────────────────
        total_views = 0
        mvt = re.search(r'"viewCountText"\s*:\s*\{"simpleText"\s*:\s*"([^"]+)"', html)
        if mvt:
            total_views = _parse_sub(re.sub(r"[^0-9만억KkMmBb.,]","", mvt.group(1)))

        # ── 영상 수 ───────────────────────────────────────────
        video_cnt = 0
        mvc = re.search(r'"videoCountText".*?"text"\s*:\s*"(\d+)"', html)
        if mvc:
            video_cnt = int(mvc.group(1))

        return {
            "title":       title or query,
            "subs":        subs,
            "total_views": total_views,
            "video_count": video_cnt,
            "desc":        desc[:100],
            "thumb":       thumb,
            "url":         url,
        }
    return None


def fetch_subs_only(channel_url: str) -> int | None:
    """구독자 수만 빠르게 재조회"""
    html = _fetch_html(channel_url)
    if not html:
        return None
    ma = re.search(r'"subscriberCount"\s*:\s*"(\d+)"', html)
    if ma:
        return int(ma.group(1))
    mb = re.search(r'"subscriberCountText"\s*:\s*\{"simpleText"\s*:\s*"([^"]+)"', html)
    if mb:
        nm = re.search(r"([\d,]+\.?\d*)\s*([만억KkMmBb]?)", mb.group(1))
        if nm:
            return _parse_sub(nm.group(0))
    return None


def estimate_per_sec(subs: int, total_views: int, video_count: int) -> float:
    """
    구독자 수·총조회수 기반으로 '초당 구독자 증가율' 추정.
    - 소형(<10만): 일 50~500명
    - 중형(10만~100만): 일 200~2000명
    - 대형(>100만): 일 1000~50000명
    외부 데이터 없이 채널 크기 기반 휴리스틱 사용.
    """
    if subs <= 0:
        return 0.0
    # 로그 스케일로 일 증가 추정
    # 참고: 구독자 100만 채널 평균 일 ~500~2000명 증가
    log_s = math.log10(max(subs, 1))
    # 기본 일 증가율 (경험적)
    base_daily = 10 ** (log_s * 0.72 - 1.2)
    # 조회수/구독자 비율로 보정 (활성 채널일수록 높음)
    if subs > 0 and total_views > 0:
        ratio = total_views / subs
        activity = min(max(ratio / 100, 0.3), 3.0)
        base_daily *= activity
    daily = max(base_daily, 1.0)
    return daily / 86400  # 초당


# ─────────────────────────────────────────────
# 유틸 함수
# ─────────────────────────────────────────────
def fmt_num(n: int) -> str:
    if n >= 100_000_000: return f"{n/100_000_000:.2f}억"
    if n >= 10_000:      return f"{n/10_000:.1f}만"
    return f"{n:,}"

def speed_label(per_hour: float) -> str:
    if per_hour >= 10_000: return "🚀 폭발적 증가"
    if per_hour >= 1_000:  return "⚡ 매우 빠름"
    if per_hour >= 100:    return "📈 빠름"
    if per_hour >= 10:     return "➡️ 보통"
    if per_hour > 0:       return "🐢 느림"
    if per_hour < 0:       return "📉 감소 중"
    return "— 변동 없음"

def calc_stats(records: list) -> dict:
    if len(records) < 2:
        return {}
    df = pd.DataFrame(records)
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.sort_values("ts")
    delta       = df["subs"].iloc[-1] - df["subs"].iloc[0]
    elapsed_sec = (df["ts"].iloc[-1] - df["ts"].iloc[0]).total_seconds()
    elapsed_min = max(elapsed_sec / 60, 1e-6)
    elapsed_hr  = max(elapsed_sec / 3600, 1e-6)
    return {
        "delta_total": delta,
        "per_min":     delta / elapsed_min,
        "per_hour":    delta / elapsed_hr,
        "per_day":     delta / elapsed_hr * 24,
        "elapsed_min": elapsed_min,
        "count":       len(records),
    }


# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ 설정")
    st.markdown("---")

    channel_query = st.text_input(
        "채널명 또는 @핸들",
        placeholder="@MrBeast  /  긱블  /  핫소스",
    )

    fetch_interval = st.select_slider(
        "실제 갱신 주기 (API 호출)",
        options=[30, 60, 120, 300, 600],
        value=60,
        format_func=lambda x: f"{x}초" if x < 60 else f"{x//60}분",
    )

    col_s, col_e = st.columns(2)
    with col_s:
        start_btn = st.button("▶ 시작", type="primary")
    with col_e:
        stop_btn  = st.button("⏹ 정지")

    if st.button("🗑 기록 초기화"):
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.rerun()

    st.markdown("---")
    st.markdown("""
<div class="info-box">
🔑 <b>API 키 불필요</b><br>
유튜브 채널 페이지를 직접 파싱합니다.<br>
별도 계정이나 API 키 없이 바로 사용 가능합니다.
</div>
<div class="warn-box">
⚠️ <b>왜 실시간 예측인가요?</b><br>
YouTube는 구독자를 <b>1,000단위 근사치</b>로만 공개합니다.<br>
예) 29,950,000명 → 29,900,000으로 표시<br><br>
그래서 실제 스냅샷은 수십 분~수 시간에 한 번씩 바뀝니다.<br>
이 앱은 <b>채널 크기 기반 증가율 모델</b>로 사이사이를 보간해<br>
실시간처럼 보여줍니다.
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 시작 버튼 처리
# ─────────────────────────────────────────────
if start_btn:
    if not channel_query:
        st.sidebar.warning("채널명을 입력해주세요.")
    else:
        with st.spinner("채널 정보 가져오는 중..."):
            info = scrape_channel(channel_query)
        if not info:
            st.sidebar.error(
                f"'{channel_query}' 채널을 찾을 수 없습니다.\n"
                "· @핸들로 입력해보세요 (예: @채널명)\n"
                "· 채널 URL을 직접 붙여넣기 해보세요"
            )
        else:
            now   = datetime.now()
            subs  = info["subs"]
            per_s = estimate_per_sec(subs, info["total_views"], info["video_count"])
            st.session_state.channel_info   = info
            st.session_state.channel_url    = info["url"]
            st.session_state.baseline       = subs
            st.session_state.per_sec        = per_s
            st.session_state.last_fetch_ts  = now
            st.session_state.last_fetch_val = subs
            st.session_state.start_ts       = now
            st.session_state.records        = [{"ts": now.isoformat(), "subs": subs}]
            st.session_state.smooth_records = [{"ts": now.isoformat(), "subs": subs}]
            st.session_state.tracking       = True

if stop_btn:
    st.session_state.tracking = False


# ─────────────────────────────────────────────
# 메인 헤더
# ─────────────────────────────────────────────
st.markdown(
    '<p style="font-family:Space Grotesk,sans-serif;font-size:2rem;font-weight:700;color:#1a1a2e;margin-bottom:0">📡 구독자 실시간 트래커</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<p style="color:#9090b0;font-size:0.9rem;margin-bottom:1.5rem">API 키 없이 YouTube 채널 구독자 증감을 실시간으로 추적합니다</p>',
    unsafe_allow_html=True
)

# 초기 안내
if not st.session_state.tracking and not st.session_state.records:
    st.markdown("""
<div style="background:#ffffff;border:1px solid #e2e6f0;border-radius:16px;padding:3rem 2rem;text-align:center;color:#9090b0;box-shadow:0 1px 4px rgba(0,0,0,0.05)">
    <div style="font-size:3rem;margin-bottom:1rem">📺</div>
    <div style="font-family:Space Grotesk,sans-serif;font-size:1.2rem;font-weight:600;color:#3a3a5c;margin-bottom:0.5rem">
        사이드바에서 채널을 입력하고 시작하세요
    </div>
    <div style="font-size:0.86rem;margin-bottom:1rem">
        채널명, @핸들, 채널 URL 모두 지원 · <b>API 키 불필요</b>
    </div>
    <div style="display:inline-flex;gap:1.5rem;font-size:0.82rem;color:#6060a0">
        <span>✅ @긱블</span><span>✅ @MrBeast</span><span>✅ https://youtube.com/@채널명</span>
    </div>
</div>
""", unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
# 트래킹 중: 실제 fetch + 보간 처리
# ─────────────────────────────────────────────
now = datetime.now()

if st.session_state.tracking:
    last_ts  = st.session_state.last_fetch_ts
    last_val = st.session_state.last_fetch_val
    elapsed  = (now - last_ts).total_seconds() if last_ts else 999

    # ── 실제 YouTube 재조회 (fetch_interval마다) ──────────────
    if elapsed >= fetch_interval:
        new_subs = fetch_subs_only(st.session_state.channel_url)
        if new_subs and new_subs > 0:
            # 실제 증가분으로 per_sec 재보정
            if elapsed > 0 and last_val:
                real_delta  = new_subs - last_val
                new_per_sec = real_delta / elapsed
                # 급격한 변화는 완화 (EMA 0.3 / 0.7)
                old_per_sec = st.session_state.per_sec
                st.session_state.per_sec = 0.3 * new_per_sec + 0.7 * old_per_sec
            st.session_state.last_fetch_ts  = now
            st.session_state.last_fetch_val = new_subs
            st.session_state.records.append({"ts": now.isoformat(), "subs": new_subs})

    # ── 보간: 초당 per_sec 만큼 표시값 증가 ──────────────────
    last_val_now = st.session_state.last_fetch_val or st.session_state.baseline
    seconds_since_fetch = (now - st.session_state.last_fetch_ts).total_seconds() if st.session_state.last_fetch_ts else 0
    interpolated = int(last_val_now + st.session_state.per_sec * seconds_since_fetch)

    # smooth_records에 추가 (5초마다)
    sr = st.session_state.smooth_records
    if not sr or (now - datetime.fromisoformat(sr[-1]["ts"])).total_seconds() >= 5:
        st.session_state.smooth_records.append({"ts": now.isoformat(), "subs": interpolated})

    display_subs = interpolated
else:
    # 정지 상태: 마지막 실제값 표시
    display_subs = st.session_state.last_fetch_val or (
        st.session_state.records[-1]["subs"] if st.session_state.records else 0
    )


# ─────────────────────────────────────────────
# 데이터 준비
# ─────────────────────────────────────────────
records  = st.session_state.records
sr       = st.session_state.smooth_records
info     = st.session_state.channel_info

if not records or not info:
    st.info("데이터를 수집 중입니다...")
    st.stop()

baseline         = st.session_state.baseline or display_subs
delta_from_start = display_subs - baseline
stats            = calc_stats(sr) if len(sr) >= 2 else {}

ch_title   = info.get("title", "채널")
ch_thumb   = info.get("thumb", "")
ch_desc    = info.get("desc", "")[:80]
started_at = datetime.fromisoformat(records[0]["ts"]).strftime("%H:%M:%S")
per_s      = st.session_state.per_sec
per_hour   = per_s * 3600


# ─────────────────────────────────────────────
# 채널 헤더
# ─────────────────────────────────────────────
thumb_html = (
    f'<img src="{ch_thumb}" style="width:44px;height:44px;border-radius:50%;border:2px solid #e2e6f0"/>'
    if ch_thumb else '<span style="font-size:2rem">📺</span>'
)
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
        <div class="ch-meta">{ch_desc or st.session_state.channel_url or ""} &nbsp;|&nbsp; 추적 시작: {started_at} &nbsp;|&nbsp; 스냅샷: {len(records)}회</div>
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.tracking:
    st.markdown('<div class="stopped-banner">⏸ 추적이 정지되었습니다. 사이드바에서 다시 시작할 수 있습니다.</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 히어로 카드 + 스탯 카드
# ─────────────────────────────────────────────
left_col, right_col = st.columns([5, 4], gap="medium")

with left_col:
    if delta_from_start > 0:
        delta_html = f'<span class="delta-positive">▲ +{delta_from_start:,} (추적 시작 이후)</span>'
    elif delta_from_start < 0:
        delta_html = f'<span class="delta-negative">▼ {delta_from_start:,} (추적 시작 이후)</span>'
    else:
        delta_html = '<span class="delta-zero">— 변동 없음 (대기 중)</span>'

    refresh_ts = datetime.fromisoformat(
        st.session_state.smooth_records[-1]["ts"]
        if st.session_state.smooth_records else records[-1]["ts"]
    ).strftime("%H:%M:%S")

    st.markdown(f"""
<div class="hero-card">
    <div class="hero-label">현재 구독자 수 (실시간 예측)</div>
    <div class="hero-number">{display_subs:,}</div>
    <div class="hero-sub">{fmt_num(display_subs)} · 갱신 {refresh_ts}</div>
    {delta_html}
</div>
""", unsafe_allow_html=True)

with right_col:
    s1, s2 = st.columns(2)
    with s1:
        color = '#16a34a' if per_hour > 0 else '#dc2626' if per_hour < 0 else '#6b7280'
        st.markdown(f"""
<div class="stat-card">
    <div class="stat-label">시간당 증감 (예측)</div>
    <div class="stat-value" style="color:{color}">{per_hour:+,.0f}</div>
    <div class="stat-sub">{speed_label(per_hour)}</div>
</div>""", unsafe_allow_html=True)
    with s2:
        per_day = per_hour * 24
        color2  = '#16a34a' if per_day > 0 else '#dc2626' if per_day < 0 else '#6b7280'
        st.markdown(f"""
<div class="stat-card">
    <div class="stat-label">일 예상 증감</div>
    <div class="stat-value" style="color:{color2}">{per_day:+,.0f}</div>
    <div class="stat-sub">현재 속도 기준</div>
</div>""", unsafe_allow_html=True)

    s3, s4 = st.columns(2)
    with s3:
        if st.session_state.start_ts:
            elapsed_sec = (now - st.session_state.start_ts).total_seconds()
            elapsed_str = f"{elapsed_sec/60:.0f}분" if elapsed_sec < 3600 else f"{elapsed_sec/3600:.1f}시간"
        else:
            elapsed_str = "—"
        st.markdown(f"""
<div class="stat-card">
    <div class="stat-label">추적 시간</div>
    <div class="stat-value">{elapsed_str}</div>
    <div class="stat-sub">스냅샷 {len(records)}회</div>
</div>""", unsafe_allow_html=True)
    with s4:
        per_min = per_s * 60
        st.markdown(f"""
<div class="stat-card">
    <div class="stat-label">분당 증감 (예측)</div>
    <div class="stat-value">{per_min:+.1f}</div>
    <div class="stat-sub">초당 {per_s:+.3f}명</div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 구독자 추이 차트 (보간 포함)
# ─────────────────────────────────────────────
if len(sr) >= 2:
    st.markdown('<p class="section-title">구독자 추이 (실시간 보간)</p>', unsafe_allow_html=True)

    df_s = pd.DataFrame(sr)
    df_s["ts"]    = pd.to_datetime(df_s["ts"])
    df_s["label"] = df_s["ts"].dt.strftime("%H:%M:%S")

    # 실제 스냅샷 포인트
    df_r = pd.DataFrame(records)
    df_r["ts"]    = pd.to_datetime(df_r["ts"])
    df_r["label"] = df_r["ts"].dt.strftime("%H:%M:%S")

    fig = go.Figure()
    # 보간 라인
    fig.add_trace(go.Scatter(
        x=df_s["label"], y=df_s["subs"],
        mode="lines", name="예측 추이",
        line=dict(color="#3b82f6", width=2.5, shape="spline"),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.07)",
        hovertemplate="<b>%{x}</b><br>예측: %{y:,}<extra></extra>",
    ))
    # 실제 스냅샷 마커
    if len(df_r) >= 1:
        fig.add_trace(go.Scatter(
            x=df_r["label"], y=df_r["subs"],
            mode="markers", name="실제 스냅샷",
            marker=dict(size=9, color="#f97316", symbol="circle",
                        line=dict(width=2, color="#ffffff")),
            hovertemplate="<b>%{x}</b><br>실제: %{y:,}<extra></extra>",
        ))
    fig.add_hline(
        y=baseline, line_dash="dot", line_color="rgba(160,160,180,0.5)",
        annotation_text=f"시작: {baseline:,}",
        annotation_font=dict(color="#9090b0", size=11),
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#ffffff",
        font=dict(color="#3a3a5c", family="Noto Sans KR"),
        margin=dict(t=20, b=30, l=10, r=10), height=300,
        xaxis=dict(showgrid=False, tickfont=dict(size=11), tickangle=-30),
        yaxis=dict(gridcolor="#f0f2f8", tickfont=dict(size=11), tickformat=","),
        hovermode="x unified",
        legend=dict(bgcolor="rgba(255,255,255,0.85)", bordercolor="#e2e6f0", borderwidth=1),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# 측정 기록 로그 (실제 스냅샷만)
# ─────────────────────────────────────────────
if records:
    st.markdown('<p class="section-title">실제 스냅샷 기록</p>', unsafe_allow_html=True)
    log_rows = ""
    for i, rec in enumerate(reversed(records[-20:])):
        ts_str = datetime.fromisoformat(rec["ts"]).strftime("%H:%M:%S")
        subs_v = rec["subs"]
        idx    = len(records) - 1 - i
        if idx > 0:
            diff = subs_v - records[idx-1]["subs"]
            if diff > 0:
                diff_html = f'<span style="color:#16a34a;font-weight:600">+{diff:,}</span>'
            elif diff < 0:
                diff_html = f'<span style="color:#dc2626;font-weight:600">{diff:,}</span>'
            else:
                diff_html = '<span style="color:#9090b0">±0 (1,000단위 동일)</span>'
        else:
            diff_html = '<span style="color:#9090b0">기준값</span>'
        log_rows += f"""
<div class="log-row">
    <span class="log-time">{ts_str}</span>
    <span style="font-family:Space Grotesk,sans-serif;font-weight:600;color:#1a1a2e">{subs_v:,}</span>
    <span>{diff_html}</span>
</div>"""

    st.markdown(f"""
<div style="background:#ffffff;border:1px solid #e2e6f0;border-radius:14px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.04)">
    <div style="display:flex;justify-content:space-between;padding:0.6rem 1rem;background:#f8faff;border-bottom:1px solid #e2e6f0;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;color:#9090b0">
        <span>시각</span><span>구독자 수 (스냅샷)</span><span>증감</span>
    </div>
    {log_rows}
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 자동 새로고침 (5초마다 보간값 업데이트)
# ─────────────────────────────────────────────
if st.session_state.tracking:
    time.sleep(5)
    st.rerun()
