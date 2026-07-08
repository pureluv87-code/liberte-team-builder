import streamlit as st
import pandas as pd
import numpy as np
import time
import os

# 1. 페이지 설정
st.set_page_config(page_title="Liberte 정기전 팀 빌더", layout="wide")

# 💡 [전체 레이아웃 및 사이드바 테마 강제 고정 CSS]
st.markdown(
    """
    <style>
    /* 0️⃣ 최상단 헤더 및 메뉴바 영역 완전 검은색 고정 */
    header[data-testid="stHeader"], 
    [data-testid="stHeader"] *,
    div[data-testid="stToolbar"],
    .stAppDeployButton {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* 1️⃣ 앱 전체 배경을 완전한 검은색(#000000)으로 강제 고정 */
    .stApp {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    h1, h2, h3, h4, h5, h6, p, span {
        color: #ffffff !important;
    }

    /* 2️⃣ 왼쪽 사이드바 영역 배경색 및 내부 글자 고정 */
    [data-testid="stSidebar"], 
    [data-testid="stSidebarContent"], 
    section[data-sidebar="true"] > div {
        background-color: #111214 !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    /* 사이드바 버튼 스타일 고정 */
    [data-testid="stSidebar"] button[data-testid="baseButton-secondary"] p,
    [data-testid="stSidebar"] button p {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] button {
        background-color: #2b2d31 !important;
        border: 1px solid #4e5058 !important;
    }

    /* 사이드바 참석 명단 표 스타일 */
    [data-testid="stSidebar"] .stDataFrame div[data-testid="stTable"] td, 
    [data-testid="stSidebar"] .stDataFrame div[data-testid="stTable"] th,
    [data-testid="stSidebar"] [data-testid="stDataFrame"] td,
    [data-testid="stSidebar"] [data-testid="stDataFrame"] th {
        padding: 2px 4px !important;
        font-size: 13px !important;
        color: #ffffff !important;
        background-color: #1a1c1e !important;
    }
    
    /* 3️⃣ 에버리지 수치 영역 라벨색 고정 */
    [data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# 로고 이미지 배치
IMAGE_NAME = "logo.jpg"
if os.path.exists(IMAGE_NAME):
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.image(IMAGE_NAME, use_container_width=True)
else:
    st.caption("💡 최상단 여백용 'logo.jpg' 파일을 app.py와 같은 폴더에 넣어주시면 로고가 표시됩니다.")

st.title("🎳 Liberte 정기전 테이블 배치")
st.write("왼쪽 메뉴에서 당일 참석자를 체크하고 아래 '🔥 팀 짜기 시작' 버튼을 누르면 팀이 편성됩니다.")
st.markdown("---")

# 2. 데이터 초기화 및 상태 관리
if "member_df" not in st.session_state:
    RAW_DATA = {
        "참석": [True] * 33,
        "이름": ["김정수", "문상원", "박진원", "박기덕", "원종혁", "정상현", "이준협", "이상현", "유현재", "강병철", "한승오", "최낙민", "안치관", "김용태", "송미연", "김지현", "조인희", "김지원", "김수진", "김민표", "추진", "윤관호", "유명선", "추송", "안호성", "정민영", "이도연", "김정아", "권혁환", "심기홍", "홍소연", "장성민", "장혜린"],
        "에버리지": [226, 218, 214, 213, 212, 210, 209, 208, 205, 205, 204, 202, 199, 198, 197, 196, 193, 191, 190, 188, 187, 186, 178, 176, 173, 170, 165, 165, 165, 158, 156, 154, 0]
    }
    st.session_state.member_df = pd.DataFrame(RAW_DATA)

# 3. 사이드바 설정 영역
st.sidebar.header("⚙️ 정기전 설정")
num_teams = st.sidebar.slider("오늘 사용할 테이블(팀) 수 지정", min_value=1, max_value=7, value=4)
show_avg = st.sidebar.toggle("📊 통합 에버리지 수치 보기", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("👥 당일 참석자 명단 편집 (칠텐 7/8 기준 에버)")

btn_col1, btn_col2 = st.sidebar.columns(2)
with btn_col1:
    if st.button("✅ 전체 선택", use_container_width=True):
        st.session_state.member_df["참석"] = True
        st.rerun()
with btn_col2:
    if st.button("⬜ 전체 해제", use_container_width=True):
        st.session_state.member_df["참석"] = False
        st.rerun()

sidebar_column_config = {
    "참석": st.column_config.CheckboxColumn("참석", width=45, default=True),
    "이름": st.column_config.TextColumn("이름", width=80, required=True),
    "에버리지": st.column_config.NumberColumn("Avg", width=55, min_value=0, max_value=300, required=True)
}

edited_df = st.sidebar.data_editor(
    st.session_state.member_df, 
    num_rows="fixed", 
    use_container_width=True,
    column_config=sidebar_column_config,
    hide_index=True,
    key="direct_team_builder_editor"
)

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("➕ 회원 추가", use_container_width=True):
        st.session_state.member_df = edited_df 
        new_row = pd.DataFrame([{"참석": True, "이름": "새회원", "에버리지": 150}])
        st.session_state.member_df = pd.concat([st.session_state.member_df, new_row], ignore_index=True)
        st.rerun()
with col2:
    if st.button("❌ 맨 아래 삭제", use_container_width=True):
        if len(edited_df) > 0:
            st.session_state.member_df = edited_df.drop(edited_df.index[-1]).reset_index(drop=True)
            st.rerun()

st.sidebar.markdown("---")

# 4. 메인 화면
if st.button("🔥 지정된 테이블 수로 팀 짜기 시작 (클릭)", type="primary", use_container_width=True):
    st.session_state.member_df = edited_df
    players = edited_df[edited_df["참석"] == True].dropna(subset=["이름", "에버리지"]).copy()
    players["에버리지"] = pd.to_numeric(players["에버리지"])
    total_players = len(players)
    
    if total_players < num_teams:
        st.error(f"🚨 현재 참석 체크된 인원({total_players}명)이 지정한 테이블 수({num_teams}개)보다 적습니다.")
    else:
        with st.spinner("🎳 Liberte 최적의 황금 밸런스 조합을 계산하는 중..."):
            time.sleep(2)
            best_teams = None
            best_diff = 999.0
            
            # 루프 강화: 10,000번 반복하여 5점 이하 조합 탐색
            for _ in range(10000):
                shuffled_players = players.sample(frac=1).reset_index(drop=True)
                temp_teams = [[] for _ in range(num_teams)]
                for idx, row in shuffled_players.iterrows():
                    temp_teams[idx % num_teams].append((row["이름"], row["에버리지"]))
                
                # 각 팀의 평균 계산
                team_averages = [np.mean([p[1] for p in t]) if t else 0 for t in temp_teams]
                current_diff = max(team_averages) - min(team_averages)
                
                # 4점 이하 조합 찾으면 즉시 중단
                if current_diff <= 4.0:
                    best_teams = temp_teams
                    best_diff = current_diff
                    break
                
                # 최선 조합 기록
                if current_diff < best_diff:
                    best_diff = current_diff
                    best_teams = temp_teams
            
            teams = best_teams
            st.info(f"📊 **오늘 총 참석 인원:** {total_players}명 | 🏟️ **배정 테이블 수:** {num_teams}개")
            
            table_cols = st.columns([1] * num_teams)
            for i in range(num_teams):
                with table_cols[i]:
                    st.markdown(f"### 🏟️ {i+1}번 테이블")
                    current_team_df = pd.DataFrame(teams[i], columns=["이름", "에버리지"])
                    
                    left_lane = [row[0] for idx, row in enumerate(teams[i]) if idx % 2 == 0]
                    right_lane = [row[0] for idx, row in enumerate(teams[i]) if idx % 2 != 0]
                    max_len = max(len(left_lane), len(right_lane))
                    while len(left_lane) < max_len: left_lane.append("")
                    while len(right_lane) < max_len: right_lane.append("")
                    
                    html_table = f"""
                    <div style="padding: 2px; background-color: #000000;">
                        <table style="width:100%; border-collapse:collapse; border:3px solid #000000; text-align:center; vertical-align:middle; background-color:#e9ecef; font-family:sans-serif; font-size:15px;">
                            <thead>
                                <tr style="background-color:#ced4da;">
                                    <th style="border:3px solid #000000; padding:8px; color:#000000; font-weight:bold; text-align:center; width:50%;">⬅️ 좌측 레인</th>
                                    <th style="border:3px solid #000000; padding:8px; color:#000000; font-weight:bold; text-align:center; width:50%;">➡️ 우측 레인</th>
                                </tr>
                            </thead>
                            <tbody>"""
                    for idx in range(max_len):
                        html_table += f"<tr><td style='border:3px solid #000000; padding:8px; color:#000000;'>{left_lane[idx]}</td><td style='border:3px solid #000000; padding:8px; color:#000000;'>{right_lane[idx]}</td></tr>"
                    html_table += "</tbody></table></div>"
                    
                    st.components.v1.html(html_table, height=(max_len * 42) + 55, scrolling=False)
                    
                    if show_avg:
                        st.metric(label="통합 에버리지", value=f"{current_team_df['에버리지'].mean():.1f} 점")