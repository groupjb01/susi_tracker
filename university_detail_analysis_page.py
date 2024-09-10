import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def university_detail_analysis(df):
    st.title("학교별 세부분석")

    universities = sorted(df['대학명'].unique())
    selected_university = st.selectbox("대학을 선택하세요", universities, key="university_detail_selectbox")

    uni_data = df[df['대학명'] == selected_university]

    for i, admission_key in enumerate(uni_data['전형명_key'].unique()):
        if i > 0:
            st.markdown("---")

        st.markdown(f"## 📊 {admission_key} 전형")

        admission_data = uni_data[uni_data['전형명_key'] == admission_key]

        competition_rate_columns = [col for col in admission_data.columns if col.startswith('경쟁률_')]
        past_data_columns = ['D-2(2024)', 'D-1(2024)', 'D-0오전(2024)', 'D-0오후(2024)', '최종(2024)', '3개년평균']

        for major in admission_data['모집단위'].unique():
            major_data = admission_data[admission_data['모집단위'] == major]

            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # 현재 경쟁률 데이터
            x = [col.split('_', 1)[1] for col in competition_rate_columns]
            y = major_data[competition_rate_columns].values[0]
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers+text', name='현재 경쟁률',
                                     line=dict(color='blue', width=3),
                                     text=[f'{val:.2f}' for val in y],
                                     textposition='top center'), secondary_y=False)

            # 과거 데이터
            colors = ['gray', 'gray', 'gray', 'gray', 'red', 'orange']
            past_y_values = []
            for col, color in zip(past_data_columns, colors):
                if col in major_data.columns and not pd.isna(major_data[col].values[0]):
                    value = major_data[col].values[0]
                    past_y_values.append(value)
                    fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[value, value], mode='lines', name=col,
                                             line=dict(color=color, width=1, dash='dot'),
                                             opacity=0.5, showlegend=False), secondary_y=True)

            # 경쟁률 6.00 기준선 추가
            fig.add_trace(go.Scatter(x=[x[0], x[-1]], y=[6, 6], mode='lines', name='경쟁률 6.00',
                                     line=dict(color='green', width=2, dash='dot'),
                                     showlegend=False))

            fig.update_layout(
                title=f"{major} - {admission_key} 전형 경쟁률 추이",
                xaxis_title="기준일",
                yaxis_title="현재 경쟁률",
                yaxis2_title="과거 경쟁률",
                height=600,
                width=1000,
                showlegend=False,  # 범례 제거
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color="rgba(0,0,0,1)"),
            )

            # y축 범위 설정
            all_y_values = list(y) + past_y_values + [6]  # 6.00 포함
            y_min, y_max = min(all_y_values), max(all_y_values)
            y_range = [max(0, y_min - 0.5), y_max + 0.5]

            # 과거 데이터 텍스트 및 경쟁률 6.00 텍스트 준비
            past_data_text = [f"<span style='color:{colors[i]}'>{col}: {major_data[col].values[0]:.2f}</span>"
                              for i, col in enumerate(past_data_columns)
                              if col in major_data.columns and not pd.isna(major_data[col].values[0])]
            past_data_vals = [major_data[col].values[0] for col in past_data_columns
                              if col in major_data.columns and not pd.isna(major_data[col].values[0])]

            # 경쟁률 6.00 텍스트 항상 추가
            all_text = past_data_text + [f"<span style='color:green'>경쟁률 6.00</span>"]
            all_vals = past_data_vals + [6]

            fig.update_yaxes(range=y_range, secondary_y=False, showgrid=False)
            fig.update_yaxes(range=y_range, secondary_y=True, showgrid=True,
                             ticktext=all_text,
                             tickvals=all_vals,
                             tickfont=dict(color="black"))
            fig.update_layout(yaxis_range=y_range, yaxis2_range=y_range)

            fig.update_xaxes(showgrid=False)

            st.plotly_chart(fig, use_container_width=True)