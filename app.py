import streamlit as st
import pandas as pd
import numpy as np
import time

# 1. 페이지 설정
st.set_page_config(page_title="Liberte 정기전 팀 빌더", layout="wide")
st.title("🎳 Liberte 정기전 레인별 팀 빌더")
st.write("왼쪽 사이드바에서 당일 참석자를 체크하고 버튼을 누르면 테이블별로 조가 편성됩니다.")

st.markdown("---")

# 2. 초기 원본 명단 고정
RAW_MEMBERS = {
    "이름": ["김정수", "문상원", "박진원", "박기덕", "이상현", "원종혁", "이준협", "정상현", "강병철", "유현재", "한승오", "최낙민", "안치관", "송미연", "김용태", "김지현", "조인희", "김수진", "김지원", "김민표", "추진", "윤관호", "유명선", "추송", "안호성", "정민영", "김정아", "권혁환", "이도연", "홍소연", "장성민"],
    "에버리지": [227, 220, 214, 213, 212, 212, 210, 208, 205, 204, 204, 202, 199, 199, 198, 195, 194, 192, 190, 188, 187, 186, 178, 176, 174, 170, 166, 165, 164, 156, 154]
}

if "member_df" not in st.session_state:
    df_init = pd.DataFrame(RAW_MEMBERS)
    df_init.insert(0, "참석", True)
    st.session_state.member_df = df_init

# 3. 사이드바 설정 영역
st.sidebar.header("⚙️ 정기전 설정")
num_teams = st.sidebar.slider("오늘 사용할 테이블(팀) 수 지정", min_value=1, max_value=6, value=4)

st.sidebar.markdown("---")
st.sidebar.subheader("👥 당일 참석자 명단 편집")
st.sidebar.write("오늘 온 회원들을 체크해 주세요.")

sidebar_column_config = {
    "참석": st.column_config.CheckboxColumn("참석", width="small", default=True),
    "이름": st.column_config.TextColumn("이름", width="medium", required=True),
    "에버리지": st.column_config.NumberColumn("Avg", width="small", min_value=0, max_value=300, required=True)
}

edited_df = st.sidebar.data_editor(
    st.session_state.member_df, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config=sidebar_column_config,
    hide_index=True,
    key="liberte_editor_v2"
)
st.session_state.member_df = edited_df

st.sidebar.markdown("---")
st.sidebar.write("💡 **안내:**")
st.sidebar.write("결과 화면에는 테이블 하단에 통합 에버리지만 표기됩니다.")

# 4. 메인 화면: 팀 빌딩 시작 버튼 및 결과 출력
if st.button("🔥 지정된 테이블 수로 팀 짜기 시작 (클릭)", type="primary", use_container_width=True):
    players = edited_df[edited_df["참석"] == True].dropna(subset=["이름", "에버리지"]).copy()
    players["에버리지"] = pd.to_numeric(players["에버리지"])
    players = players.sort_values(by="에버리지", ascending=False).reset_index(drop=True)
    
    total_players = len(players)
    
    if total_players < num_teams:
        st.error(f"🚨 현재 참석 체크된 인원({total_players}명)이 지정한 테이블 수({num_teams}개)보다 적습니다. 왼쪽 메뉴에서 테이블 수를 줄이거나 참석 인원을 더 체크해 주세요.")
    else:
        try:
            with st.spinner("🎳 Liberte 최적의 레인 조합을 계산하는 중... 잠시만 기다려주세요."):
                time.sleep(1.2)
                
                teams = [[] for _ in range(num_teams)]
                bottom_players = players.tail(num_teams).sample(frac=1).reset_index(drop=True)
                remaining_players = players.head(total_players - num_teams).copy()
                
                shuffled_remaining = []
                for i in range(0, len(remaining_players), num_teams):
                    chunk = remaining_players.iloc[i:i+num_teams].sample(frac=1)
                    shuffled_remaining.append(chunk)
                remaining_players = pd.concat(shuffled_remaining).reset_index(drop=True)
                
                for i in range(num_teams):
                    teams[i].append((bottom_players.loc[i, "이름"], bottom_players.loc[i, "에버리지"]))
                    
                for idx, row in remaining_players.iterrows():
                    turn = idx // num_teams
                    step = idx % num_teams
                    if turn % 2 == 0:
                        team_idx = step
                    else:
                        team_idx = num_teams - 1 - step
                    
                    teams[team_idx].append((row["이름"], row["에버리지"]))
                    
            st.success(f"📊 배정 완료: 오늘 총 **{total_players}명** 참석 ➡️ **{num_teams}개 테이블** 배치 완료")
            
            table_cols = st.columns([1] * num_teams)
            for i in range(num_teams):
                with table_cols[i]:
                    st.markdown(f"### 🏟️ {i+1}번 테이블")
                    current_team_df = pd.DataFrame(teams[i], columns=["이름", "에버리지"]).sort_values(by="에버리지", ascending=False).reset_index(drop=True)
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