import streamlit as st
import pandas as pd
import numpy as np
import time

# 1. 페이지 설정
st.set_page_config(page_title="Liberte 정기전 팀 빌더", layout="wide")

# 사이드바 내부 표의 간격과 글자 크기 촘촘하게 조절
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] .stDataFrame div[data-testid="stTable"] td, 
    [data-testid="stSidebar"] .stDataFrame div[data-testid="stTable"] th {
        padding: 2px 4px !important;
        font-size: 13px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🎳 Liberte 정기전 레인별 팀 빌더")
st.write("왼쪽 메뉴에서 당일 참석자를 체크하고 아래 '🔥 팀 짜기 시작' 버튼을 누르면 조가 편성됩니다.")

st.markdown("---")

# 2. 초기 원본 명단 고정 (기본 데이터)
RAW_DATA = {
    "참석": [True] * 31,
    "이름": ["김정수", "문상원", "박진원", "박기덕", "이상현", "원종혁", "이준협", "정상현", "강병철", "유현재", "한승오", "최낙민", "안치관", "송미연", "김용태", "김지현", "조인희", "김수진", "김지원", "김민표", "추진", "윤관호", "유명선", "추송", "안호성", "정민영", "김정아", "권혁환", "이도연", "홍소연", "장성민"],
    "에버리지": [227, 220, 214, 213, 212, 212, 210, 208, 205, 204, 204, 202, 199, 199, 198, 195, 194, 192, 190, 188, 187, 186, 178, 176, 174, 170, 166, 165, 164, 156, 154]
}

if "member_df" not in st.session_state:
    st.session_state.member_df = pd.DataFrame(RAW_DATA)

# 3. 사이드바 설정 영역
st.sidebar.header("⚙️ 정기전 설정")
num_teams = st.sidebar.slider("오늘 사용할 테이블(팀) 수 지정", min_value=1, max_value=7, value=4)

st.sidebar.markdown("---")
st.sidebar.subheader("👥 당일 참석자 명단 편집")

# 전체 선택/해제 버튼
btn_col1, btn_col2 = st.sidebar.columns(2)
with btn_col1:
    if st.button("✅ 전체 선택", use_container_width=True):
        st.session_state.member_df["참석"] = True
        st.rerun()
with btn_col2:
    if st.button("⬜ 전체 해제", use_container_width=True):
        st.session_state.member_df["참석"] = False
        st.rerun()

# 열 너비 촘촘하게 세팅
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
    key="liberte_speed_master_editor"
)

# 회원 추가/삭제 버튼
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("➕ 회원 추가", use_container_width=True):
        new_row = pd.DataFrame([{"참석": True, "이름": "새회원", "에버리지": 150}])
        st.session_state.member_df = pd.concat([st.session_state.member_df, new_row], ignore_index=True)
        st.rerun()
with col2:
    if st.button("❌ 맨 아래 삭제", use_container_width=True):
        if len(st.session_state.member_df) > 0:
            st.session_state.member_df = st.session_state.member_df.drop(st.session_state.member_df.index[-1])
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("💡 **안내:** 결과 화면에는 테이블별 조편성과 통합 에버리지만 표기됩니다.")

# 4. 메인 화면: 팀 빌딩 시작 버튼 및 결과 출력
if st.button("🔥 지정된 테이블 수로 팀 짜기 시작 (클릭)", type="primary", use_container_width=True):
    st.session_state.member_df = edited_df
    
    players = edited_df[edited_df["참석"] == True].dropna(subset=["이름", "에버리지"]).copy()
    players["에버리지"] = pd.to_numeric(players["에버리지"])
    
    total_players = len(players)
    
    if total_players < num_teams:
        st.error(f"🚨 현재 참석 체크된 인원({total_players}명)이 지정한 테이블 수({num_teams}개)보다 적습니다. 왼쪽 메뉴에서 테이블 수를 줄이거나 참석 인원을 더 체크해 주세요.")
    else:
        try:
            with st.spinner("🎳 Liberte 최적의 황금 밸런스 조합을 계산하는 중..."):
                time.sleep(3)
                
                best_teams = None
                best_diff = 999.0
                
                # 최대 5000번 최적의 조합 시뮬레이션
                for _ in range(5000):
                    shuffled_players = players.sample(frac=1).reset_index(drop=True)
                    
                    temp_teams = [[] for _ in range(num_teams)]
                    for idx, row in shuffled_players.iterrows():
                        temp_teams[idx % num_teams].append((row["이름"], row["에버리지"]))
                    
                    team_averages = []
                    for t in temp_teams:
                        avgs = [p[1] for p in t]
                        team_averages.append(np.mean(avgs) if avgs else 0)
                    
                    current_diff = max(team_averages) - min(team_averages)
                    
                    if current_diff <= 5.0:
                        best_teams = temp_teams
                        best_diff = current_diff
                        break
                    
                    if current_diff < best_diff:
                        best_diff = current_diff
                        best_teams = temp_teams
                
                teams = best_teams

            table_cols = st.columns([1] * num_teams)
            for i in range(num_teams):
                with table_cols[i]:
                    st.markdown(f"### 🏟️ {i+1}번 테이블")
                    
                    # 💡 [핵심 수정]: 팀 내 에버리지 정렬 코드를 삭제하고, 배정된 멤버를 한 번 더 무작위(.sample(frac=1))로 섞습니다.
                    current_team_df = pd.DataFrame(teams[i], columns=["이름", "에버리지"]).sample(frac=1).reset_index(drop=True)
                    total_avg = current_team_df["에버리지"].mean()
                    
                    left_lane = []
                    right_lane = []
                    for idx, row in current_team_df.iterrows():
                        if idx % 2 == 0:
                            left_lane.append(row["이름"])
                        else:
                            right_lane.append(row["이름"])
                    
                    max_len = max(len(left_lane), len(right_lane))
                    while len(left_lane) < max_len: left_lane.append("")
                    while len(right_lane) < max_len: right_lane.append("")
                    
                    combined_table = pd.DataFrame({
                        "⬅️ 좌측 레인": left_lane,
                        "➡️ 우측 레인": right_lane
                    })
                    st.dataframe(combined_table, use_container_width=True, hide_index=True)
                    st.metric(label="통합 에버리지", value=f"{total_avg:.1f} 점")
                    
        except Exception as e:
            st.error(f"❌ 팀 구성 도중 알 수 없는 에러가 발생했습니다: {e}")