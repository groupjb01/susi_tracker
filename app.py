import streamlit as st
import pandas as pd
from dashboard_page import dashboard
from university_analysis_page import university_analysis
from university_detail_analysis_page import university_detail_analysis
from filtering_search_page import filtering_search  # 새로 추가된 import


# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv('integrated_data.csv')
    return df


def main():
    st.title("🖋️ 지략 수시 경쟁률 Tracker 📊")

    # 타이틀과 탭 사이에 줄바꿈 추가
    st.markdown("<br>", unsafe_allow_html=True)

    df = load_data()

    # 탭 생성 및 스타일 적용
    tabs = st.tabs(["대시보드", "학교별 통합분석", "학교별 세부분석", "필터링 검색", "보고서 생성"])

    # CSS를 사용하여 탭 너비를 전체 페이지에 맞게 조정
    st.markdown("""
        <style>
            .stTabs [data-baseweb="tab-list"] {
                gap: 0px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #F0F2F6;
                border-radius: 4px 4px 0px 0px;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
                flex-grow: 1;
                flex-basis: 0;
                font-size: 14px;
            }
            .stTabs [aria-selected="true"] {
                background-color: #FFFFFF;
            }
        </style>
    """, unsafe_allow_html=True)

    with tabs[0]:
        dashboard(df)

    with tabs[1]:
        university_analysis(df)

    with tabs[2]:
        university_detail_analysis(df)

    with tabs[3]:
        filtering_search(df)  # 새로 추가된 함수 호출

    with tabs[4]:
        st.header("보고서 생성")
        st.write("이 페이지는 개발 중입니다.")


if __name__ == "__main__":
    main()
