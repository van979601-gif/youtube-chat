import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from wordcloud import WordCloud
from youtube_comment_downloader import YoutubeCommentDownloader
from collections import Counter
import re
import os
import urllib.request

# -----------------------------
# 한글 폰트 자동 다운로드 및 설정
# (Streamlit Cloud 대응)
# -----------------------------
FONT_PATH = "/tmp/NotoSansKR-Regular.otf"
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf"

# 폰트 파일이 없으면 다운로드
if not os.path.exists(FONT_PATH):
    try:
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
    except Exception:
        # fallback: 다른 CDN에서 시도
        fallback_url = "https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2107@1.1/Pretendard-Regular.woff"
        try:
            urllib.request.urlretrieve(fallback_url, FONT_PATH)
        except Exception:
            FONT_PATH = None

# matplotlib 한글 폰트 적용
if FONT_PATH and os.path.exists(FONT_PATH):
    fm.fontManager.addfont(FONT_PATH)
    font_name = fm.FontProperties(fname=FONT_PATH).get_name()
    plt.rcParams["font.family"] = font_name
else:
    # 시스템에 설치된 한글 폰트 탐색
    for f in fm.findSystemFonts():
        if any(k in f.lower() for k in ["nanum", "gothic", "malgun", "korean"]):
            fm.fontManager.addfont(f)
            plt.rcParams["font.family"] = fm.FontProperties(fname=f).get_name()
            FONT_PATH = f
            break

plt.rcParams["axes.unicode_minus"] = False

# -----------------------------
# Streamlit 기본 설정
# -----------------------------
st.set_page_config(
    page_title="YouTube 댓글 분석기",
    layout="wide"
)

st.title("📺 YouTube 댓글 분석 대시보드")
st.markdown("유튜브 영상 댓글을 수집하고 사용자 반응을 분석합니다.")

# -----------------------------
# 유튜브 URL 입력
# -----------------------------
video_url = st.text_input(
    "유튜브 영상 링크를 입력하세요",
    placeholder="https://www.youtube.com/watch?v=..."
)

# 댓글 수 슬라이더
comment_limit = st.slider(
    "수집할 댓글 수",
    min_value=20,
    max_value=10000,
    value=500,
    step=20
)

# -----------------------------
# 댓글 수집 함수
# -----------------------------
@st.cache_data
def get_comments(video_url, limit):
    downloader = YoutubeCommentDownloader()
    comments = []
    count = 0
    for comment in downloader.get_comments_from_url(video_url):
        comments.append({
            "text": comment["text"],
            "likes": comment.get("votes", 0),
            "time": comment.get("time", "")
        })
        count += 1
        if count >= limit:
            break
    return pd.DataFrame(comments)

# -----------------------------
# 좋아요 숫자 변환 함수
# -----------------------------
def convert_likes(x):
    x = str(x).replace(",", "").upper()
    if "K" in x:
        return float(x.replace("K", "")) * 1000
    elif "M" in x:
        return float(x.replace("M", "")) * 1000000
    try:
        return float(x)
    except Exception:
        return 0

# -----------------------------
# 폰트 prop 헬퍼
# -----------------------------
def get_font_prop(size=10):
    if FONT_PATH and os.path.exists(FONT_PATH):
        return fm.FontProperties(fname=FONT_PATH, size=size)
    return fm.FontProperties(size=size)

# -----------------------------
# 분석 시작 버튼
# -----------------------------
if st.button("댓글 수집 및 분석 시작"):

    if not video_url:
        st.warning("유튜브 링크를 입력해주세요.")
        st.stop()

    with st.spinner("댓글 수집 중입니다..."):
        try:
            df = get_comments(video_url, comment_limit)
            df["likes"] = df["likes"].apply(convert_likes)
            if df.empty:
                st.error("댓글을 가져오지 못했습니다.")
                st.stop()
            st.success(f"{len(df)}개의 댓글을 수집했습니다.")
        except Exception as e:
            st.error(f"오류 발생: {e}")
            st.stop()

    fp = get_font_prop()

    # -----------------------------
    # 데이터 미리보기
    # -----------------------------
    st.subheader("📄 수집된 댓글 데이터")
    st.dataframe(df.head(20), use_container_width=True)

    # -----------------------------
    # 좋아요 수 분석
    # -----------------------------
    st.subheader("👍 댓글 좋아요 수 분석")
    col1, col2, col3 = st.columns(3)
    col1.metric("평균 좋아요", round(df["likes"].mean(), 2))
    col2.metric("최대 좋아요", int(df["likes"].max()))
    col3.metric("총 좋아요", int(df["likes"].sum()))

    # -----------------------------
    # 좋아요 TOP 10 댓글 그래프
    # -----------------------------
    st.subheader("🔥 좋아요 TOP 10 댓글")

    top_likes = df.sort_values(by="likes", ascending=False).head(10)
    labels = top_likes["text"].str[:30].tolist()

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        data=top_likes,
        x="likes",
        y=labels,
        palette="Reds_r",
        ax=ax
    )

    # 한글 폰트를 틱 라벨에 명시 적용
    ax.set_title("좋아요 TOP 10 댓글", fontproperties=get_font_prop(13))
    ax.set_xlabel("좋아요 수", fontproperties=fp)
    ax.set_ylabel("댓글", fontproperties=fp)
    ax.set_yticklabels(labels, fontproperties=get_font_prop(9))
    ax.set_xticklabels(ax.get_xticklabels(), fontproperties=fp)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # -----------------------------
    # 시간대별 댓글 추이
    # -----------------------------
    st.subheader("⏰ 시간대별 댓글 추이")

    def extract_hour(time_str):
        if isinstance(time_str, str):
            match = re.search(r'(\d+)\s+hour', time_str)
            if match:
                return int(match.group(1))
        return None

    df["hour"] = df["time"].apply(extract_hour)
    hour_df = df.dropna(subset=["hour"])

    if not hour_df.empty:
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        sns.countplot(data=hour_df, x="hour", palette="Blues", ax=ax2)
        ax2.set_title("시간 기준 댓글 분포", fontproperties=get_font_prop(13))
        ax2.set_xlabel("시간 전", fontproperties=fp)
        ax2.set_ylabel("댓글 수", fontproperties=fp)
        ax2.set_xticklabels(ax2.get_xticklabels(), fontproperties=fp)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.info("시간 데이터 분석이 제한됩니다.")

    # -----------------------------
    # 워드클라우드
    # -----------------------------
    st.subheader("☁️ 자주 등장하는 단어")

    text_data = " ".join(df["text"].astype(str))
    text_data = re.sub(r"http\S+", "", text_data)
    text_data = re.sub(r"[^가-힣a-zA-Z\s]", "", text_data)

    stopwords = {
        "the", "and", "is", "to",
        "이", "그", "저", "것",
        "진짜", "너무", "정말"
    }

    wc_kwargs = dict(
        width=1200,
        height=600,
        background_color="white",
        stopwords=stopwords,
        colormap="Reds",
    )
    # 폰트가 있을 때만 font_path 전달
    if FONT_PATH and os.path.exists(FONT_PATH):
        wc_kwargs["font_path"] = FONT_PATH

    try:
        wordcloud = WordCloud(**wc_kwargs).generate(text_data)
        fig3, ax3 = plt.subplots(figsize=(15, 7))
        ax3.imshow(wordcloud, interpolation="bilinear")
        ax3.axis("off")
        fig3.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)
    except Exception as e:
        st.warning(f"워드클라우드 생성 실패: {e}")

    # -----------------------------
    # 자주 등장한 단어 TOP 20
    # -----------------------------
    st.subheader("🔤 자주 등장한 단어 TOP 20")

    words = text_data.split()
    filtered_words = [w for w in words if len(w) > 1 and w not in stopwords]
    word_freq = Counter(filtered_words)
    top_words = pd.DataFrame(
        word_freq.most_common(20),
        columns=["단어", "빈도"]
    )

    fig4, ax4 = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top_words, x="빈도", y="단어", palette="viridis", ax=ax4)
    ax4.set_title("TOP 20 단어", fontproperties=get_font_prop(13))
    ax4.set_xlabel("빈도", fontproperties=fp)
    ax4.set_ylabel("단어", fontproperties=fp)
    ax4.set_yticklabels(top_words["단어"].tolist(), fontproperties=get_font_prop(9))
    ax4.set_xticklabels(ax4.get_xticklabels(), fontproperties=fp)
    fig4.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)
