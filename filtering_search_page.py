import streamlit as st
import pandas as pd
import numpy as np


def get_university_emoji(university_name):
    # 대학 이름에 따라 적절한 이모티콘을 반환하는 함수
    # 여기에 더 많은 대학을 추가할 수 있습니다
    emoji_dict = {
        "서울대학교": "🏛️",
        "연세대학교": "🎓",
        "고려대학교": "🦅",
        "성균관대학교": "📚",
        "서강대학교": "🌟",
        "한양대학교": "🔬",
        "중앙대학교": "🏫",
        "경희대학교": "🌸",
        "한국외국어대학교": "🌎",
        "서울시립대학교": "🏙️",
    }
    return emoji_dict.get(university_name, "🏫")  # 기본 이모티콘


def filtering_search(df):
    st.header("필터링 검색")

    # 1단계: 계열 선택
    series_option = st.radio(
        "계열 선택",
        ["모두", "인문", "자연"],
        key="filtering_series_radio"
    )

    # 2단계: 대상 학교 선택
    universities = sorted(df['대학명'].unique())
    selected_universities = st.multiselect(
        "대상 학교 선택 (복수 선택 가능)",
        universities,
        key="filtering_universities_multiselect"
    )

    # 3단계: 경쟁률 필터 및 추천전형 필터
    max_competition_rate = st.number_input(
        "경쟁률 필터 (이하)",
        min_value=0.0,
        max_value=100.0,
        value=6.00,
        step=0.01,
        format="%.2f",
        key="filtering_competition_rate_input"
    )

    only_recommended = st.checkbox(
        "추천전형만 보기",
        key="filtering_recommended_checkbox"
    )

    # 탐색 버튼
    if st.button("탐색", key="filtering_search_button"):
        if not selected_universities:
            st.warning("최소 하나의 대학을 선택해주세요.")
        else:
            # 데이터 필터링
            filtered_df = df[df['대학명'].isin(selected_universities)]

            # 최신 경쟁률 컬럼 찾기
            latest_competition_rate = [col for col in df.columns if col.startswith('경쟁률_')][-1]

            filtered_df = filtered_df[filtered_df[latest_competition_rate] <= max_competition_rate]

            # 계열 필터링
            if series_option != "모두":
                filtered_df = filtered_df[filtered_df['계열'] == series_option]

            if only_recommended:
                filtered_df = filtered_df[filtered_df['추천전형'] == 1]

            # 결과 표시
            if filtered_df.empty:
                st.info("조건에 맞는 결과가 없습니다.")
            else:
                for univ in selected_universities:
                    st.markdown("---")  # 학교가 바뀔 때 구분선 추가
                    emoji = get_university_emoji(univ)
                    st.subheader(f"{emoji} {univ}")
                    univ_df = filtered_df[filtered_df['대학명'] == univ]

                    for admission_type, symbol in [('교과', '📌'), ('종합', '🔍')]:
                        admission_df = univ_df[univ_df['전형구분'] == admission_type]
                        if not admission_df.empty:
                            st.write(f"{symbol} {admission_type} 전형")
                            columns_to_show = ['모집단위', '전형명', '모집인원', latest_competition_rate, '최종(2024)', '3개년평균']

                            # 최신 경쟁률 기준으로 내림차순 정렬
                            admission_df_sorted = admission_df.sort_values(by=latest_competition_rate, ascending=False)

                            st.dataframe(
                                admission_df_sorted[columns_to_show].rename(columns={latest_competition_rate: '최신경쟁률'}),
                                hide_index=True,
                                width=None  # 화면 너비에 맞춤
                            )
                        else:
                            st.write(f"{symbol} {admission_type} 전형: 해당 없음")

    # 전체 페이지의 글씨 크기를 조정하는 CSS
    st.markdown("""
            <style>
                .stDataFrame {
                    font-size: 0.8rem;
                }
                .stDataFrame td, .stDataFrame th {
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    max-width: 150px;
                }
            </style>
            """, unsafe_allow_html=True)