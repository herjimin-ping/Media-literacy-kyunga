import streamlit as st
import pandas as pd
import plotly.express as px
import feedparser
import urllib.parse
import re

# ------------------------------------------------------------
# 기본 페이지 설정
# ------------------------------------------------------------
st.set_page_config(
    page_title="미디어 리터러시 진단 & 뉴스 팩트체크",
    page_icon="🧭",
    layout="wide",
)

st.title("🧭 미디어 리터러시 진단 & 실시간 뉴스 팩트체크")
st.caption("나의 정보 판별 유형을 알아보고, 실시간 뉴스로 직접 팩트체크 연습을 해보세요.")

tab1, tab2 = st.tabs(["🧪 미디어 리터러시 유형 테스트", "📰 실시간 뉴스 팩트체크"])

# ==============================================================
# 탭 1. 미디어 리터러시 유형 테스트
# ==============================================================
with tab1:
    st.header("🧪 나의 미디어 리터러시 유형은?")
    st.write("아래 8개 문항에 답하면 유형과 맞춤 학습 팁을 알려드려요.")

    # 각 문항: (질문, 축, 방향)
    # 축1: speed  -> "빠름"(+1) vs "신중함"(-1)
    # 축2: basis  -> "감정"(+1) vs "근거"(-1)
    questions = [
        ("뉴스 제목만 보고 바로 판단을 내리는 편이다.", "speed", 1),
        ("기사를 읽기 전에 원문 출처부터 확인하는 편이다.", "speed", -1),
        ("자극적인 제목의 기사를 보면 일단 눌러보게 된다.", "speed", 1),
        ("공유하기 전에 사실 여부를 검색해보는 편이다.", "speed", -1),
        ("기사를 읽고 나면 감정적으로 먼저 반응한다.", "basis", 1),
        ("통계나 데이터가 없는 주장은 잘 믿지 않는다.", "basis", -1),
        ("댓글 반응을 보고 기사에 대한 판단을 정하기도 한다.", "basis", 1),
        ("같은 사안에 대해 여러 매체를 비교해보는 편이다.", "basis", -1),
    ]

    answers = {}
    with st.form("mlq_form"):
        for i, (q, axis, direction) in enumerate(questions):
            answers[i] = st.slider(q, min_value=1, max_value=5, value=3, key=f"q{i}",
                                    help="1: 전혀 아니다 ~ 5: 매우 그렇다")
        submitted = st.form_submit_button("결과 확인하기")

    if submitted:
        speed_score = 0
        basis_score = 0
        for i, (q, axis, direction) in enumerate(questions):
            centered = answers[i] - 3  # -2 ~ +2
            if axis == "speed":
                speed_score += centered * direction
            else:
                basis_score += centered * direction

        # 유형 판정
        speed_type = "속독형" if speed_score >= 0 else "신중형"
        basis_type = "감성형" if basis_score >= 0 else "근거형"

        type_map = {
            ("속독형", "감성형"): {
                "name": "🚀 빠른 공감러",
                "desc": "정보를 빠르게 받아들이고 감정적으로 먼저 반응하는 유형이에요. 공유 속도는 빠르지만 오정보에 취약할 수 있어요.",
                "tips": [
                    "공유 전에 '5초만 멈추기' 습관을 들여보세요.",
                    "제목만 보고 판단하지 말고 본문을 끝까지 읽어보세요.",
                    "감정이 크게 요동치는 기사일수록 출처를 다시 확인하세요.",
                ],
            },
            ("속독형", "근거형"): {
                "name": "⚡ 스피드 팩트체커",
                "desc": "정보 습득은 빠르지만 근거를 중시하는 유형이에요. 다만 속도 때문에 검증이 얕아질 수 있어요.",
                "tips": [
                    "빠른 판단은 좋지만, 최소 1개의 다른 매체와 비교해보세요.",
                    "통계나 인용의 원출처(1차 자료)를 확인하는 습관을 들이세요.",
                    "팩트체크 사이트(예: SNU 팩트체크)를 즐겨찾기 해두세요.",
                ],
            },
            ("신중형", "감성형"): {
                "name": "🌙 느낌적 신중러",
                "desc": "판단은 신중하지만 최종 결정은 감정에 기대는 유형이에요. 검증 습관에 감정 필터를 더하면 좋아요.",
                "tips": [
                    "판단 전에 '이 감정이 사실 판단에 영향을 주고 있진 않은가?' 자문해보세요.",
                    "감정적으로 동의하는 기사일수록 반대 시각의 기사도 찾아보세요.",
                    "신중한 태도를 살려 출처의 신뢰도 등급을 매겨보는 연습을 해보세요.",
                ],
            },
            ("신중형", "근거형"): {
                "name": "🔍 정통 팩트체커",
                "desc": "정보를 신중하게, 근거 중심으로 판단하는 유형이에요. 이미 좋은 습관을 갖고 있어요!",
                "tips": [
                    "지금의 습관을 주변에도 나눠보세요 (팩트체크 방법 공유).",
                    "너무 많은 검증 과정으로 정보 피로가 오지 않도록 신뢰할 출처 목록을 미리 정해두세요.",
                    "새로운 매체나 플랫폼의 신뢰도도 주기적으로 재평가해보세요.",
                ],
            },
        }

        result = type_map[(speed_type, basis_type)]

        st.divider()
        st.subheader(f"결과: {result['name']}")
        st.write(result["desc"])

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                x=["신중함 ← → 속독", "근거중심 ← → 감성중심"],
                y=[speed_score, basis_score],
                labels={"x": "축", "y": "점수"},
                color=["speed", "basis"],
            )
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**맞춤 학습 팁**")
            for tip in result["tips"]:
                st.markdown(f"- {tip}")

# ==============================================================
# 탭 2. 실시간 뉴스 팩트체크 대시보드
# ==============================================================
with tab2:
    st.header("📰 실시간 뉴스 팩트체크 연습")
    st.write("키워드를 입력하면 구글 뉴스에서 실시간 헤드라인을 가져와 분석해드려요.")

    keyword = st.text_input("검색 키워드를 입력하세요", value="인공지능")
    num_articles = st.slider("가져올 기사 수", min_value=5, max_value=30, value=15)

    SENSATIONAL_WORDS = [
        "충격", "경악", "발칵", "논란", "결국", "단독", "속보",
        "긴급", "폭로", "파문", "초유", "역대급", "대박", "충격적",
    ]

    @st.cache_data(ttl=600)
    def fetch_news(keyword, n):
        query = urllib.parse.quote(keyword)
        url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        rows = []
        for entry in feed.entries[:n]:
            title = entry.get("title", "")
            source = ""
            if " - " in title:
                source = title.split(" - ")[-1]
            published = entry.get("published", "")
            link = entry.get("link", "")
            rows.append({"제목": title, "출처": source, "게시일": published, "링크": link})
        return pd.DataFrame(rows)

    def sensational_score(title):
        score = 0
        score += title.count("!") * 1
        score += sum(1 for w in SENSATIONAL_WORDS if w in title)
        if re.search(r"[가-힣]{2,}\?\?", title):
            score += 1
        return score

    if keyword:
        with st.spinner("실시간 뉴스를 불러오는 중..."):
            news_df = fetch_news(keyword, num_articles)

        if news_df.empty:
            st.warning("뉴스를 불러오지 못했습니다. 다른 키워드로 시도해보세요.")
        else:
            news_df["자극도 점수"] = news_df["제목"].apply(sensational_score)

            st.subheader("📌 헤드라인 목록")
            st.dataframe(
                news_df[["제목", "출처", "게시일", "자극도 점수"]],
                use_container_width=True,
                column_config={"링크": st.column_config.LinkColumn()},
            )

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🔥 제목 자극도 분포")
                fig_score = px.bar(
                    news_df.sort_values("자극도 점수", ascending=False).head(10),
                    x="자극도 점수",
                    y="제목",
                    orientation="h",
                )
                fig_score.update_layout(height=450, yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_score, use_container_width=True)

            with col2:
                st.subheader("🏢 출처(매체) 다양성")
                source_counts = news_df["출처"].value_counts().reset_index()
                source_counts.columns = ["출처", "건수"]
                fig_source = px.pie(source_counts, names="출처", values="건수")
                fig_source.update_layout(height=450)
                st.plotly_chart(fig_source, use_container_width=True)

            st.divider()
            st.subheader("✅ 팩트체크 셀프 체크리스트")
            st.markdown(
                """
                - [ ] 같은 사안을 다룬 매체가 **3곳 이상**인가요?
                - [ ] 제목에 자극적인 표현(느낌표, '충격', '단독' 등)이 과도하지 않나요?
                - [ ] 기사에 **1차 출처(통계, 발표, 인터뷰)**가 명시되어 있나요?
                - [ ] 작성 시간이 최신인가요, 오래된 기사가 재유통된 것은 아닌가요?
                - [ ] 이 정보를 공유하기 전에 반대 입장의 기사도 확인했나요?
                """
            )
