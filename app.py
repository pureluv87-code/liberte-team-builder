import streamlit as st
import pandas as pd
import numpy as np
import time
import os

# 1. 페이지 설정
st.set_page_config(page_title="Liberte 정기전 팀 빌더", layout="wide")

# 💡 [CSS 스타일]
st.markdown(
    """
    <style>
    header[data-testid="stHeader"], [data-testid="stHeader"] *, div[data-testid="stToolbar"], .stAppDeployButton {
        background-color: #000000 !important; color: #ffffff !important;
    }
    .stApp { background-color: #000000 !important; color: #ffffff !important; }
    h1, h2, h3, h4, h5, h6, p, span { color: #ffffff !important; }
    [data-testid="stSidebar"], [data-testid="stSidebarContent"], section[data-sidebar="true"] > div {
        background-color: #111214 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] button {
        background-color: #2b2d31 !important; border: 1px solid #4e5058 !important;
    }
    [data-testid="stSidebar"] .stDataFrame td, [data-testid="stSidebar"] .stDataFrame th {
        padding: 2px 4px !important; font-size: 13px !important; color: #ffffff !important; background-color: #1a1c1e !important;
    }
    [data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# 로고
IMAGE_NAME = "logo.jpg"
if os.path.exists(IMAGE_NAME):
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.image(IMAGE_NAME, use_container_width=True)

st.title("🎳 Liberte 정기전 테이블 배치")
st.write("왼쪽 메뉴에서 당일 참석자를 체크하고 아래 버튼을 누르면 팀이 편성됩니다.")
st.markdown("---")

# 데이터 초기화
if "member_df" not in st.session_state:
    RAW_DATA = {
        "참석": [True] * 33,
        "이름": ["김정수", "문상원", "박진원", "박기덕", "원종혁", "정상현", "이준협", "이상현", "유현재", "강병철", "한승오", "최낙민", "안치관", "김용태", "송미연", "김지현", "조인희", "김지원", "김수진", "김민표", "추진", "윤관호", "유명선", "추송", "안호성", "정민영", "이도연", "김정아", "권혁환", "심기홍", "홍소연", "장성민", "장혜린"],
        "에버리지": [226, 218, 214, 213, 212, 210, 209, 208, 205, 205, 204, 202, 199, 198, 197, 196, 193, 191, 190, 188, 187, 186, 178, 176, 173, 170, 165, 165, 165, 158, 156, 154, 0]
    }
    st.session_state.member_df = pd.DataFrame(RAW_DATA)

# 3. 사이드바 설정
st.sidebar.header("⚙️ 정기전 설정")
num_teams = st.sidebar.slider("오늘 사용할 테이블(팀) 수 지정", 1, 7, 4)
use_balance = st.sidebar.toggle("⚖️ 에버리지 밸런스 맞춤 사용", value=True)
show_avg = st.sidebar.toggle("📊 통합 에버리지 수치 보기", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("👥 당일 참석자 명단 편집")

btn_col1, btn_col2 = st.sidebar.columns(2)
if btn_col1.button("✅ 전체 선택"):
    st.session_state.member_df["참석"] = True; st.rerun()
if btn_col2.button("⬜ 전체 해제"):
    st.session_state.member_df["참석"] = False; st.rerun()

edited_df = st.sidebar.data_editor(st.session_state.member_df, use_container_width=True, hide_index=True)

col1, col2 = st.sidebar.columns(2)
if col1.button("➕ 회원 추가"):
    st.session_state.member_df = pd.concat([edited_df, pd.DataFrame([{"참석": True, "이름": "새회원", "에버리지": 150}])], ignore_index=True)
    st.rerun()
if col2.button("❌ 맨 아래 삭제"):
    st.session_state.member_df = edited_df.drop(edited_df.index[-1]).reset_index(drop=True)
    st.rerun()

# 4. 메인 팀 배정
if st.button("🔥 팀 짜기 시작 (클릭)", type="primary", use_container_width=True):
    players = edited_df[edited_df["참석"] == True].dropna(subset=["이름", "에버리지"]).copy()
    players["에버리지"] = pd.to_numeric(players["에버리지"])
    
    if len(players) < num_teams:
        st.error("참석 인원이 부족합니다.")
    else:
        with st.spinner("🎳 팀 배정 중..."):
            if use_balance:
                # [수정된 밸런스 로직]
                best_teams = None; best_diff = 999.0
                for _ in range(10000):
                    shuffled_players = players.sample(frac=1).reset_index(drop=True)
                    temp_teams = [[] for _ in range(num_teams)]
                    for idx, row in shuffled_players.iterrows():
                        temp_teams[idx % num_teams].append((row["이름"], row["에버리지"]))
                    
                    team_averages = [np.mean([p[1] for p in t]) if t else 0 for t in temp_teams]
                    current_diff = max(team_averages) - min(team_averages)
                    
                    if current_diff <= 4.0:
                        best_teams = temp_teams
                        break
                    if current_diff < best_diff:
                        best_diff = current_diff
                        best_teams = temp_teams
                teams = best_teams
            else:
                # [랜덤 배정 로직]
                shuffled = players.sample(frac=1).values
                teams = [[] for _ in range(num_teams)]
                for idx, row in enumerate(shuffled): teams[idx % num_teams].append((row[1], row[2]))
            
            # 결과 출력
            table_cols = st.columns([1] * num_teams)
            for i in range(num_teams):
                with table_cols[i]:
                    st.markdown(f"### 🏟️ {i+1}번 테이블")
                    current_team_df = pd.DataFrame(teams[i], columns=["이름", "에버리지"])
                    
                    left = [row[0] for idx, row in enumerate(teams[i]) if idx % 2 == 0]
                    right = [row[0] for idx, row in enumerate(teams[i]) if idx % 2 != 0]
                    max_l = max(len(left), len(right))
                    while len(left) < max_l: left.append("")
                    while len(right) < max_l: right.append("")
                    
                    html = "<table style='width:100%; border-collapse:collapse; background:#e9ecef; text-align:center;'>"
                    html += "<thead><tr style='background:#ced4da;'><th style='border:1px solid #000; padding:5px;'>⬅️ 좌측</th><th style='border:1px solid #000; padding:5px;'>➡️ 우측</th></tr></thead><tbody>"
                    for idx in range(max_l):
                        html += f"<tr><td style='border:1px solid #000; padding:5px; color:#000;'>{left[idx]}</td><td style='border:1px solid #000; padding:5px; color:#000;'>{right[idx]}</td></tr>"
                    html += "</tbody></table>"
                    st.components.v1.html(html, height=(max_l * 40) + 50, scrolling=False)
                    
                    if show_avg:
                        st.metric("통합 에버리지", f"{current_team_df['에버리지'].mean():.1f} 점")