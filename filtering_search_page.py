import streamlit as st
import pandas as pd
import numpy as np


@st.cache_data
def get_university_emoji(university_name):
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
    return emoji_dict.get(university_name, "🏫")


@st.cache_data
def filter_data(df, selected_universities, max_competition_rate, series_option, only_recommended,
                latest_competition_rate):
    filtered_df = df[df['대학명'].isin(selected_universities)]
    filtered_df = filtered_df[filtered_df[latest_competition_rate] <= max_competition_rate]

    if series_option != "모두":
        filtered_df = filtered_df[filtered_df['계열'] == series_option]

    if only_recommended:
        filtered_df = filtered_df[filtered_df['추천전형'] == 1]

    return filtered_df


def filtering_search(df, universities):
    st.header("필터링 검색")

    series_option = st.radio("계열 선택", ["모두", "인문", "자연"], key="filtering_series_radio")

    selected_universities = st.multiselect("대상 학교 선택 (복수 선택 가능)", universities,
                                           key="filtering_universities_multiselect")

    max_competition_rate = st.number_input("경쟁률 필터 (이하)", min_value=0.0, max_value=100.0, value=6.00, step=0.01,
                                           format="%.2f", key="filtering_competition_rate_input")

    only_recommended = st.checkbox("추천전형만 보기", key="filtering_recommended_checkbox")

    if st.button("탐색", key="filtering_search_button"):
        if not selected_universities:
            st.warning("최소 하나의 대학을 선택해주세요.")
        else:
            latest_competition_rate = [col for col in df.columns if col.startswith('경쟁률_')][-1]
            filtered_df = filter_data(df, selected_universities, max_competition_rate, series_option, only_recommended,
                                      latest_competition_rate)

            if filtered_df.empty:
                st.info("조건에 맞는 결과가 없습니다.")
            else:
                for univ in selected_universities:
                    st.markdown("---")
                    emoji = get_university_emoji(univ)
                    st.subheader(f"{emoji} {univ}")
                    univ_df = filtered_df[filtered_df['대학명'] == univ]

                    for admission_type, symbol in [('교과', '📌'), ('종합', '🔍')]:
                        admission_df = univ_df[univ_df['전형구분'] == admission_type]
                        if not admission_df.empty:
                            st.write(f"{symbol} {admission_type} 전형")
                            columns_to_show = ['모집단위', '전형명', '모집인원', latest_competition_rate, '최종(2024)', '3개년평균']

                            admission_df_sorted = admission_df.sort_values(by=latest_competition_rate, ascending=False)

                            st.dataframe(
                                admission_df_sorted[columns_to_show].rename(columns={latest_competition_rate: '최신경쟁률'}),
                                hide_index=True,
                                width=None
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
