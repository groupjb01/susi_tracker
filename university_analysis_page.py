import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random


def get_emoji_for_admission(admission_key):
    emoji_dict = {
        "학생부교과": "📚", "학생부종합": "🎓", "논술": "✍️", "실기/실적": "🎭",
        "수능": "📝", "학생부교과(지역인재)": "🏠", "학생부종합(지역인재)": "🌄"
    }
    return emoji_dict.get(admission_key, "📊")  # 기본 이모티콘은 📊


def generate_distinct_colors(n):
    colors = []
    for i in range(n):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        colors.append(f'rgb({r},{g},{b})')
    return colors


def university_analysis(df):
    st.title("학교별 분석")

    universities = sorted(df['대학명'].unique())
    selected_university = st.selectbox("대학을 선택하세요", universities)

    uni_data = df[df['대학명'] == selected_university]

    competition_rate_columns = [col for col in df.columns if col.startswith('경쟁률_')]
    latest_competition_rate = competition_rate_columns[-1]

    previous_competition_rate = competition_rate_columns[-2] if len(competition_rate_columns) > 1 else None

    for admission_key in uni_data['전형명_key'].unique():
        emoji = get_emoji_for_admission(admission_key)
        st.markdown(f"### {emoji} {admission_key} 전형")

        admission_data = uni_data[uni_data['전형명_key'] == admission_key]

        fig = go.Figure()

        top_5 = admission_data.nlargest(5, latest_competition_rate)['모집단위'].tolist()

        # 색상 생성
        colors = generate_distinct_colors(len(admission_data['모집단위'].unique()))

        annotations = []
        for i, major in enumerate(admission_data['모집단위'].unique()):
            major_data = admission_data[admission_data['모집단위'] == major]

            x = []
            y = []
            for col in competition_rate_columns:
                value = major_data[col].values[0]
                if pd.notna(value):
                    x.append(col.split('_', 1)[1])
                    y.append(value)

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines+markers',
                name=major,
                hovertemplate='%{y:.2f}<extra></extra>',
                line=dict(color=colors[i])
            ))

            # 상위 5개 모집단위에 대해 주석 추가 (오른쪽에 한 번만)
            if major in top_5:
                last_y = y[-1]
                annotations.append(dict(
                    x=1.02, y=last_y,
                    xref='paper', yref='y',
                    text=f'{major} ({last_y:.2f})',
                    font=dict(size=8),
                    showarrow=False,
                    xanchor='left',
                    yanchor='middle'
                ))

        fig.update_layout(
            title=f"{admission_key} 전형 경쟁률 추이",
            xaxis_title="기준일",
            yaxis_title="경쟁률",
            height=700,
            margin=dict(l=50, r=120, t=100, b=200),  # 오른쪽 여백 증가
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(size=6),
                itemsizing='constant',
                itemwidth=30,
                tracegroupgap=2
            ),
            hovermode="x unified",
            annotations=annotations,
            xaxis=dict(domain=[0, 0.9])  # x축 영역을 줄여 오른쪽에 공간 확보
        )

        st.plotly_chart(fig, use_container_width=True)

        # 경쟁률 상위 5개, 하위 5개 표 생성
        columns_to_select = ['모집단위', '모집인원', latest_competition_rate]
        if previous_competition_rate:
            columns_to_select.append(previous_competition_rate)

        top_5_df = admission_data.nlargest(5, latest_competition_rate)[columns_to_select]
        bottom_5_df = admission_data.nsmallest(5, latest_competition_rate)[columns_to_select]

        top_5_df['구분'] = 'TOP 5'
        bottom_5_df['구분'] = 'LOW 5'

        combined_df = pd.concat([top_5_df, bottom_5_df])
        combined_df = combined_df.rename(columns={
            latest_competition_rate: '현재 경쟁률'
        })

        if previous_competition_rate:
            combined_df = combined_df.rename(columns={previous_competition_rate: '이전 경쟁률'})
            combined_df['변화율(%)'] = (
                        (combined_df['현재 경쟁률'] - combined_df['이전 경쟁률']) / combined_df['이전 경쟁률'] * 100).round(2)
        else:
            combined_df['변화율(%)'] = 0.0

        # 컬럼 순서 조정 및 포맷팅
        combined_df = combined_df[['구분', '모집단위', '모집인원', '현재 경쟁률', '변화율(%)']]
        combined_df['현재 경쟁률'] = combined_df['현재 경쟁률'].round(2)

        # TOP 5와 LOW 5를 좌우로 배치
        col1, col2 = st.columns(2)

        def dataframe_to_html(df, title):
            html = f"<h5>{title}</h5>"
            html += "<table style='width:100%; font-size:0.6rem; border-collapse: collapse;'>"
            html += "<tr>" + "".join(
                f"<th style='border:1px solid black; padding:5px;'>{col}</th>" for col in df.columns) + "</tr>"
            for _, row in df.iterrows():
                html += "<tr>" + "".join(
                    f"<td style='border:1px solid black; padding:5px;'>{row[col]}</td>" for col in df.columns) + "</tr>"
            html += "</table>"
            return html

        with col1:
            st.markdown(dataframe_to_html(combined_df[combined_df['구분'] == 'TOP 5'].drop('구분', axis=1), "TOP 5"),
                        unsafe_allow_html=True)

        with col2:
            st.markdown(dataframe_to_html(combined_df[combined_df['구분'] == 'LOW 5'].drop('구분', axis=1), "LOW 5"),
                        unsafe_allow_html=True)

        st.markdown("---")  # 전형 끝에 구분선 추가

    # 전체 페이지의 글씨 크기를 조정하는 CSS
    st.markdown("""
        <style>
            .stDataFrame {
                font-size: 0.7rem;
            }
            body {
                font-size: 0.8rem;
            }
        </style>
        """, unsafe_allow_html=True)