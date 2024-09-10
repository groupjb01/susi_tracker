import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# 대학 그룹 정의
university_groups = {
    "서연고": ["서울대학교", "연세대학교", "고려대학교"],
    "서성한": ["서강대학교", "성균관대학교", "한양대학교"],
    "중경외시이": ["중앙대학교", "경희대학교", "한국외국어대학교", "서울시립대학교", "이화여자대학교"],
    "경건동홍숙": ["경희대학교", "건국대학교", "동국대학교", "홍익대학교", "숙명여자대학교"],
    "국숭세단/과기/인하/아주": ["국민대학교", "숭실대학교", "세종대학교", "단국대학교(죽전)", "서울과학기술대학교", "인하대학교", "아주대학교"],
    "성신/광운/가천/가톨릭/에리카": ["성신여자대학교", "광운대학교", "가천대학교", "가톨릭대학교", "한양대학교(에리카)"],
    "명지/상명/항공/경기/글로벌/인천": ["명지대학교", "상명대학교", "경기대학교", "한국외국어대학교(글로벌)", "인천대학교", "한국항공대학교"],
    "동덕/덕성/서울여대": ["동덕여자대학교", "덕성여자대학교", "서울여자대학교"],
}


def dashboard(df):
    st.markdown("<br>", unsafe_allow_html=True)
    # 경쟁률 컬럼 찾기
    competition_rate_columns = [col for col in df.columns if col.startswith('경쟁률_')]
    latest_competition_rate = competition_rate_columns[-1]

    # 1. 학교별 평균 경쟁률 (통합)
    st.markdown("### 📊 학교별 평균 경쟁률 (통합)")
    avg_competition = df.groupby('대학명')[latest_competition_rate].mean().sort_values(ascending=False)
    fig = go.Figure(go.Bar(x=avg_competition.index, y=avg_competition.values))
    fig.update_layout(title="학교별 평균 경쟁률", xaxis_title="대학명", yaxis_title="평균 경쟁률", yaxis=dict(range=[0, max(avg_competition.values) * 1.1]))
    st.plotly_chart(fig)

    st.markdown("---")

    # 2. 그룹별 평균 경쟁률 (종합/교과)
    st.markdown("### 🏫 그룹별 평균 경쟁률 (종합/교과)")
    for group, universities in university_groups.items():
        st.markdown(f"#### 🔹 {group}")

        col1, col2 = st.columns(2)

        with col1:
            # 교과전형
            fig_edu = go.Figure()
            for univ in universities:
                univ_data = df[(df['대학명'] == univ) & (df['전형구분'] == '교과')]
                x_values = [col.split('_', 1)[1] for col in competition_rate_columns]
                y_values = [univ_data[col].mean() for col in competition_rate_columns]
                fig_edu.add_trace(go.Scatter(x=x_values, y=y_values, mode='lines+markers', name=univ))
            fig_edu.update_layout(title="교과전형 평균 경쟁률", xaxis_title="기준일", yaxis_title="평균 경쟁률", height=400, yaxis=dict(range=[0, None]))
            st.plotly_chart(fig_edu, use_container_width=True)

        with col2:
            # 종합전형
            fig_comp = go.Figure()
            for univ in universities:
                univ_data = df[(df['대학명'] == univ) & (df['전형구분'] == '종합')]
                x_values = [col.split('_', 1)[1] for col in competition_rate_columns]
                y_values = [univ_data[col].mean() for col in competition_rate_columns]
                fig_comp.add_trace(go.Scatter(x=x_values, y=y_values, mode='lines+markers', name=univ))
            fig_comp.update_layout(title="종합전형 평균 경쟁률", xaxis_title="기준일", yaxis_title="평균 경쟁률", height=400, yaxis=dict(range=[0, None]))
            st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")

    # 학교장 추천전형 경쟁률 부분
    st.markdown("### 🎓 학교장 추천전형 경쟁률")
    fig_recommend = go.Figure()

    # 최신 경쟁률 컬럼 찾기
    latest_competition_rate = [col for col in df.columns if col.startswith('경쟁률_')][-1]

    # 학교별 평균 경쟁률 계산
    avg_recommend_rates = df[df['추천전형'] == 1].groupby('대학명')[latest_competition_rate].mean()

    # 상위 5개 대학 찾기
    top_5_universities = avg_recommend_rates.nlargest(5)

    annotations = []
    for univ in df['대학명'].unique():
        univ_data = df[(df['대학명'] == univ) & (df['추천전형'] == 1)]
        if not univ_data.empty:
            x_values = [col.split('_', 1)[1] for col in competition_rate_columns]
            y_values = [univ_data[col].mean() for col in competition_rate_columns]
            line = fig_recommend.add_trace(go.Scatter(x=x_values, y=y_values, mode='lines+markers', name=univ))

            # 상위 5개 대학에 대해 주석 추가
            if univ in top_5_universities.index:
                last_y = y_values[-1]
                annotations.append(dict(
                    x=1.02, y=last_y,
                    xref='paper', yref='y',
                    text=f'{univ} ({last_y:.2f})',
                    font=dict(size=10),
                    showarrow=False,
                    xanchor='left',
                    yanchor='middle'
                ))

    fig_recommend.update_layout(
        title="학교장 추천전형 평균 경쟁률",
        yaxis_title="평균 경쟁률",
        yaxis=dict(range=[0, None]),
        xaxis=dict(
            title="기준일",
            titlefont=dict(size=12),
            tickfont=dict(size=10),
            domain=[0, 0.9]  # x축 영역을 줄여 오른쪽에 공간 확보
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.45,
            font=dict(size=8)
        ),
        margin=dict(l=50, r=120, t=50, b=150),  # 오른쪽 여백 증가
        height=700,
        annotations=annotations
    )

    st.plotly_chart(fig_recommend, use_container_width=True)

    # 상위 5개, 하위 5개 경쟁률 표 수정
    top_5 = avg_recommend_rates.nlargest(5).reset_index()
    top_5.columns = ['대학명', '평균 경쟁률']
    bottom_5 = avg_recommend_rates.nsmallest(5).reset_index()
    bottom_5.columns = ['대학명', '평균 경쟁률']

    col1, col2 = st.columns(2)

    def dataframe_to_html(df, title):
        html = f"<h5>{title}</h5>"  # h4를 h3로 변경하여 크기를 키움
        html += "<table style='width:100%; font-size:0.8rem; border-collapse: collapse;'>"
        html += "<tr>" + "".join(
            f"<th style='border:1px solid black; padding:5px;'>{col}</th>" for col in df.columns) + "</tr>"
        for _, row in df.iterrows():
            html += "<tr>"
            for col in df.columns:
                value = row[col]
                if isinstance(value, float):
                    formatted_value = f"{value:.2f}"
                else:
                    formatted_value = str(value)
                html += f"<td style='border:1px solid black; padding:5px;'>{formatted_value}</td>"
            html += "</tr>"
        html += "</table>"
        return html

    with col1:
        st.markdown(dataframe_to_html(top_5, "TOP 5"), unsafe_allow_html=True)

    with col2:
        st.markdown(dataframe_to_html(bottom_5, "LOW 5"), unsafe_allow_html=True)
