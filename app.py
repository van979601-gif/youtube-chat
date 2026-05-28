import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from youtube_comment_downloader import YoutubeCommentDownloader
from collections import Counter
import re

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

    except:
        return 0

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

            # 좋아요 숫자형 변환
            df["likes"] = df["likes"].apply(convert_likes)

            if df.empty:
                st.error("댓글을 가져오지 못했습니다.")
                st.stop()

            st.success(f"{len(df)}개의 댓글을 수집했습니다.")

        except Exception as e:
            st.error(f"오류 발생: {e}")
            st.stop()

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
    # 좋아요 TOP 댓글 그래프
    # -----------------------------
    st.subheader("🔥 좋아요 TOP 10 댓글")

    top_likes = df.sort_values(
        by="likes",
        ascending=False
    ).head(10)

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.barplot(
        data=top_likes,
        x="likes",
        y=top_likes["text"].str[:30],
        palette="Reds_r",
        ax=ax
    )

    ax.set_title("좋아요 TOP 10 댓글")
    ax.set_xlabel("좋아요 수")
    ax.set_ylabel("댓글")

    st.pyplot(fig)

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

        sns.countplot(
            data=hour_df,
            x="hour",
            palette="Blues",
            ax=ax2
        )

        ax2.set_title("시간 기준 댓글 분포")
        ax2.set_xlabel("시간 전")
        ax2.set_ylabel("댓글 수")

        st.pyplot(fig2)

    else:
        st.info("시간 데이터 분석이 제한됩니다.")

    # -----------------------------
    # 워드클라우드
    # -----------------------------
    st.subheader("☁️ 자주 등장하는 단어")

    text_data = " ".join(df["text"].astype(str))

    # 텍스트 전처리
    text_data = re.sub(r"http\S+", "", text_data)
    text_data = re.sub(r"[^가-힣a-zA-Z\s]", "", text_data)

    stopwords = {
        "the", "and", "is", "to",
        "이", "그", "저", "것",
        "진짜", "너무", "정말"
    }

    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color="white",
        stopwords=stopwords,
        font_path="NanumGothic.ttf"
    ).generate(text_data)

    fig3, ax3 = plt.subplots(figsize=(15, 7))

    ax3.imshow(wordcloud, interpolation="bilinear")
    ax3.axis("off")

    st.pyplot(fig3)

    # -----------------------------
    # 자주 등장한 단어 TOP 20
    # -----------------------------
    st.subheader("🔤 자주 등장한 단어 TOP 20")

    words = text_data.split()

    filtered_words = [
        word for word in words
        if len(word) > 1 and word not in stopwords
    ]

    word_freq = Counter(filtered_words)

    top_words = pd.DataFrame(
        word_freq.most_common(20),
        columns=["단어", "빈도"]
    )

    fig4, ax4 = plt.subplots(figsize=(10, 6))

    sns.barplot(
        data=top_words,
        x="빈도",
        y="단어",
        palette="viridis",
        ax=ax4
    )

    ax4.set_title("TOP 20 단어")

    st.pyplot(fig4)
