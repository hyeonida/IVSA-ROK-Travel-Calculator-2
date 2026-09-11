import streamlit as st
import os

# 페이지 설정
st.set_page_config(
    page_title="IVSA 임원진 교통비 환급 계산기",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 스타일 커스텀
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #0F52BA;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0A3D91;
        color: white;
    }
    .result-box {
        background-color: #F0F4F8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #0F52BA;
        margin-top: 1.5rem;
    }
    .rule-box {
        background-color: #FFF9E6;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 5px solid #FFAA00;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💳 IVSA 임원진 교통비 환급 계산기")
st.write("본인의 **출발지/도착지 및 이동수단(버스, 기차, 비행기)**을 선택하면 규정에 맞춰 가산금 및 초과 감액이 자동으로 통합 산출됩니다.")

# 맵 이미지 표시
map_path = "ivsa_travel_map_v2.png"
if os.path.exists(map_path):
    st.image(map_path, caption="IVSA 전국 수의과대학 공식 노선도 및 참고 요금 기준", use_container_width=True)
elif os.path.exists("/workspace/artifacts/ivsa_travel_map_v2.png"):
    st.image("/workspace/artifacts/ivsa_travel_map_v2.png", caption="IVSA 전국 수의과대학 공식 노선도 및 참고 요금 기준", use_container_width=True)

# 핵심 규정 안내
with st.expander("📌 IVSA 교통비 환급 핵심 규정 요약 (항공/기차 포함)"):
    st.markdown("""
    * **기본 원칙:** 실제 이용 교통수단(KTX, 비행기 등)과 관계없이 **도시 간 우등 고속버스 요금**을 기준으로 지급합니다.
    * **소요 시간 가산금 (편도당):**
        * 편도 소요 시간 **2시간 30분 이상 ~ 3시간 30분 미만**: 편도 요금 +10,000원 추가
        * 편도 소요 시간 **3시간 30분 이상**: 편도 요금 +15,000원 추가
    * **항공편(비행기) 가산금 및 한도 특례:**
        * 비행기 이용 시 소요 시간과 관계없이 **편도당 +15,000원**의 가산금이 부여됩니다.
    * **5만원 초과 감액 공식:**
        * 총 기준액($X$)이 50,000원을 초과할 경우: $(X - 50,000) / 2 + 50,000$
    """)

st.write("---")

# 위치 목록 정의
LOCATIONS = [
    "서울경부 / 서울센트럴 (행사장소)",
    "동서울 (행사장소)",
    "춘천 (강원대)",
    "진주 (경상대)",
    "광주유스퀘어 (전남대)",
    "동대구터미널 (경북대)",
    "청주 (충북대)",
    "세종 (충북대)",
    "대전 (충남대)",
    "유성 (충남대)",
    "익산 (전북대)",
    "제주공항 (제주대)",
    "기타 (직접 입력)"
]

# 버스 노선 데이터베이스
ROUTES_DATABASE = {
    ("춘천 (강원대)", "서울경부 / 서울센트럴 (행사장소)"): {"fare": 10100, "duration": "2시간 30분 미만 (추가금 없음)", "desc": "춘천 ↔ 서울 일반/시외버스 기준 (약 1시간 10분)"},
    ("춘천 (강원대)", "동서울 (행사장소)"): {"fare": 8600, "duration": "2시간 30분 미만 (추가금 없음)", "desc": "춘천 ↔ 동서울 일반/시외버스 기준 (약 1시간 10분)"},
    ("진주 (경상대)", "서울경부 / 서울센트럴 (행사장소)"): {"fare": 34500, "duration": "3시간 30분 이상 (편도 +15,000원 가산)", "desc": "편도 소요시간 3시간 45분 적용"},
    ("진주 (경상대)", "동서울 (행사장소)"): {"fare": 35900, "duration": "3시간 30분 이상 (편도 +15,000원 가산)", "desc": "편도 소요시간 3시간 55분 적용"},
    ("광주유스퀘어 (전남대)", "서울경부 / 서울센트럴 (행사장소)"): {"fare": 30800, "duration": "2시간 30분 이상 - 3시간 30분 미만 (편도 +10,000원 가산)", "desc": "편도 소요시간 3시간 20분 적용"},
    ("광주유스퀘어 (전남대)", "동서울 (행사장소)"): {"fare": 33300, "duration": "3시간 30분 이상 (편도 +15,000원 가산)", "desc": "편도 소요시간 3시간 30분 적용"},
    ("동대구터미널 (경북대)", "서울경부 / 서울센트럴 (행사장소)"): {"fare": 30000, "duration": "3시간 30분 이상 (편도 +15,000원 가산)", "desc": "편도 소요시간 3시간 30분 적용"},
    ("동대구터미널 (경북대)", "동서울 (행사장소)"): {"fare": 30200, "duration": "3시간 30분 이상 (편도 +15,000원 가산)", "desc": "편도 소요시간 3시간 30분 적용"},
    ("청주 (충북대)", "서울경부 / 서울센트럴 (행사장소)"): {"fare": 13300, "duration": "2시간 30분 미만 (추가금 없음)", "desc": "편도 소요시간 1시간 30분 적용"},
    ("청주 (충북대)", "동서울 (행사장소)"): {"fare": 13300, "duration": "2시간 30분 미만 (추가금 없음)", "desc": "편도 소요시간 1시간 30분 적용"},
    ("세종 (충북대)", "서울경부 / 서울센트럴 (행사장소)"): {"fare": 14400, "duration": "2시간 30분 미만 (추가금 없음)", "desc": "편도 소요시간 1시간 40분"},
    ("세종 (충북대)", "동서울 (행사장소)"): {"fare": 16300, "duration": "2시간 30분 미만 (추가금 없음)", "desc": "편도 소요시간 2시간 10분"},
    ("대전 (충남대)", "서울경부 / 서울센트럴 (행사장소)"): {"fare": 16600, "duration": "2시간 30분 미만 (추가금 없음)", "desc": "편도 소요시간 2시간"},
    ("대전 (충남대)", "동서울 (행사장소)"): {"fare": 18100, "duration": "2시간 30분 미만 (추가금 없음)", "desc": "편도 소요시간 2시간"},
    ("유성 (충남대)", "서울경부 / 서울센트럴 (행사장소)"): {"fare": 16900, "duration": "2시간 30분 미만 (추가금 없음)", "desc": "편도 소요시간 1시간 50분"},
    ("유성 (충남대)", "동서울 (행사장소)"): {"fare": 17200, "duration": "2시간 30분 이상 - 3시간 30분 미만 (편도 +10,000원 가산)", "desc": "편도 소요시간 2시간 30분"},
    ("익산 (전북대)", "서울경부 / 서울센트럴 (행사장소)"): {"fare": 21500, "duration": "2시간 30분 이상 - 3시간 30분 미만 (편도 +10,000원 가산)", "desc": "편도 소요시간 2시간 40분"},
    ("익산 (전북대)", "동서울 (행사장소)"): {"fare": 26000, "duration": "2시간 30분 이상 - 3시간 30분 미만 (편도 +10,000원 가산)", "desc": "편도 소요시간 2시간 40분"}
}

def lookup_bus_route(dep, dest):
    if dep == dest:
        return {"fare": 0, "duration": "2시간 30분 미만 (추가금 없음)", "desc": "출발지와 도착지가 같습니다."}
    if "제주공항" in dep or "제주공항" in dest:
        return {"fare": 0, "is_jeju": True, "duration": "비행기 (편도 +15,000원 항공 가산)", "desc": "제주대 항공편 정산 대상"}
    if "기타" in dep or "기타" in dest:
        return {"fare": 0, "is_manual": True, "duration": "직접 선택", "desc": "요금과 소요시간을 직접 기입합니다."}
        
    pair = (dep, dest)
    rev_pair = (dest, dep)
    if pair in ROUTES_DATABASE:
        return ROUTES_DATABASE[pair]
    elif rev_pair in ROUTES_DATABASE:
        return ROUTES_DATABASE[rev_pair]
    return {"fare": 0, "is_manual": True, "duration": "직접 선택", "desc": "등록된 직통 우등 노선 정보가 없습니다. 직접 기입으로 전환됩니다."}

# 여정 유형 선택
trip_pattern = st.radio(
    "🧭 여정 유형을 선택해 주세요",
    options=["왕복", "편도", "가는 편과 오는 편의 경로/수단이 다름 (복합)"],
    index=0,
    horizontal=True,
    key="trip_pattern_v13"
)

st.write("")

if trip_pattern in ["왕복", "편도"]:
    st.subheader("📍 여정 경로 및 이동 수단 설정")
    
    col_mode, col_blank = st.columns([1, 1])
    with col_mode:
        trans_mode = st.radio(
            "이동 수단 유형",
            options=["고속버스 / 기차(KTX/SRT 등)", "비행기 (항공편)"],
            index=0,
            key="trans_mode_single"
        )
        
    if trans_mode == "비행기 (항공편)":
        st.info("✈️ **항공편 특례 적용:** 비행기 결제 금액에 편도당 15,000원이 추가됩니다")
        
        is_round = (trip_pattern == "왕복 (동일 경로 왕복)")
        flight_fare = st.number_input(
            "실제 비행기표 결제 총 금액 (영수증 결제액, 원)",
            min_value=0,
            value=120000 if is_round else 60000,
            step=1000,
            key="flight_fare_single_input"
        )
        
        flight_bonus = 30000 if is_round else 15000
        total_x = flight_fare + flight_bonus
        total_actual_spent = flight_fare
        flight_bonus_total = flight_bonus
        
        fare1, add1 = flight_fare / (2 if is_round else 1), 15000
        fare2, add2 = (flight_fare / 2, 15000) if is_round else (0, 0)
        mode1, mode2 = "비행기", "비행기" if is_round else "None"
        
    else: # 고속버스 / 기차
        col_dep, col_dest = st.columns(2)
        with col_dep:
            dep = st.selectbox("출발지 선택", options=LOCATIONS, index=2, key="dep_single")
        with col_dest:
            dest = st.selectbox("도착지 선택", options=LOCATIONS, index=0, key="dest_single")
            
        route_info = lookup_bus_route(dep, dest)
        is_manual = route_info.get("is_manual", False)
        
        st.caption(f"💡 **선택 노선 우등 버스 정보:** {route_info['desc']}")
        
        fare1 = st.number_input(
            "편도당 우등 버스 기준 요금 (원)",
            min_value=0,
            value=route_info["fare"] if not is_manual else 13300,
            step=100,
            disabled=not is_manual,
            key=f"fare_s_{dep}_{dest}"
        )
        
        dur_options = [
            "2시간 30분 미만 (추가금 없음)",
            "2시간 30분 이상 - 3시간 30분 미만 (편도 +10,000원 가산)",
            "3시간 30분 이상 (편도 +15,000원 가산)"
        ]
        
        default_dur_idx = 0
        if "3시간 30분 이상" in route_info["duration"]:
            default_dur_idx = 2
        elif "2시간 30분 이상" in route_info["duration"]:
            default_dur_idx = 1
            
        duration_choice = st.selectbox(
            "소요 시간 가산 기준",
            options=dur_options,
            index=default_dur_idx if not is_manual else 0,
            disabled=not is_manual,
            key=f"dur_s_{dep}_{dest}"
        )
        
        is_round = (trip_pattern == "왕복 (동일 경로 왕복)")
        
        actual_spent_input = st.number_input(
            "실제 교통비로 지출한 총 금액 (영수증 총합, 원)",
            min_value=0,
            value=int(fare1 * 2) if is_round else int(fare1),
            step=100,
            key=f"actual_s_{dep}_{dest}_{is_round}"
        )
        
        add1 = 15000 if "3시간 30분 이상" in duration_choice else (10000 if "2시간 30분 이상" in duration_choice else 0)
        
        if is_round:
            total_x = (fare1 + add1) * 2
            fare2, add2 = fare1, add1
        else:
            total_x = fare1 + add1
            fare2, add2 = 0, 0
            
        total_actual_spent = actual_spent_input
        flight_bonus_total = 0
        mode1, mode2 = "버스/기차", "버스/기차" if is_round else "None"

else: # 복합 여정 (가는 편 / 오는 편 다름)
    st.subheader("🛫 가는 편 경로 및 이동 수단")
    col_mode1, col_dep1, col_dest1 = st.columns([1.2, 1, 1])
    with col_mode1:
        mode1 = st.selectbox("가는 편 수단", options=["고속버스 / 기차", "비행기 (항공편)"], index=0, key="mode1_multi")
        
    if mode1 == "비행기 (항공편)":
        flight_fare1 = st.number_input("가는 편 비행기 결제액 (원)", min_value=0, value=60000, step=1000, key="ff1_m")
        fare1 = flight_fare1
        add1 = 15000
        actual_spent1 = flight_fare1
        st.caption("✈️ 항공 추가금 +15,000원 자동 반영")
    else:
        with col_dep1:
            dep1 = st.selectbox("가는 편 출발지", options=LOCATIONS, index=2, key="dep1_m")
        with col_dest1:
            dest1 = st.selectbox("가는 편 도착지", options=LOCATIONS, index=0, key="dest1_m")
            
        route_info1 = lookup_bus_route(dep1, dest1)
        is_manual1 = route_info1.get("is_manual", False)
        
        fare1 = st.number_input(
            "가는 편 우등 버스 요금 (원)",
            min_value=0,
            value=route_info1["fare"] if not is_manual1 else 13300,
            step=100,
            disabled=not is_manual1,
            key=f"fare1_m_{dep1}_{dest1}"
        )
        
        dur_options = [
            "2시간 30분 미만 (추가금 없음)",
            "2시간 30분 이상 - 3시간 30분 미만 (편도 +10,000원 가산)",
            "3시간 30분 이상 (편도 +15,000원 가산)"
        ]
        
        def_idx1 = 2 if "3시간 30분 이상" in route_info1["duration"] else (1 if "2시간 30분 이상" in route_info1["duration"] else 0)
        dur1_choice = st.selectbox("가는 편 소요시간 가산", options=dur_options, index=def_idx1 if not is_manual1 else 0, disabled=not is_manual1, key=f"dur1_m_{dep1}_{dest1}")
        add1 = 15000 if "3시간 30분 이상" in dur1_choice else (10000 if "2시간 30분 이상" in dur1_choice else 0)
        actual_spent1 = fare1

    st.write("---")
    st.subheader("🛬 오는 편 경로 및 이동 수단 (Inbound)")
    col_mode2, col_dep2, col_dest2 = st.columns([1.2, 1, 1])
    with col_mode2:
        mode2 = st.selectbox("오는 편 수단", options=["고속버스 / 기차", "비행기 (항공편)"], index=0, key="mode2_multi")
        
    if mode2 == "비행기 (항공편)":
        flight_fare2 = st.number_input("오는 편 비행기 결제액 (원)", min_value=0, value=60000, step=1000, key="ff2_m")
        fare2 = flight_fare2
        add2 = 15000
        actual_spent2 = flight_fare2
        st.caption("✈️ 항공 추가금 +15,000원 자동 반영")
    else:
        with col_dep2:
            dep2 = st.selectbox("오는 편 출발지", options=LOCATIONS, index=0, key="dep2_m")
        with col_dest2:
            dest2 = st.selectbox("오는 편 도착지", options=LOCATIONS, index=2, key="dest2_m")
            
        route_info2 = lookup_bus_route(dep2, dest2)
        is_manual2 = route_info2.get("is_manual", False)
        
        fare2 = st.number_input(
            "오는 편 우등 버스 요금 (원)",
            min_value=0,
            value=route_info2["fare"] if not is_manual2 else 13300,
            step=100,
            disabled=not is_manual2,
            key=f"fare2_m_{dep2}_{dest2}"
        )
        
        dur_options = [
            "2시간 30분 미만 (추가금 없음)",
            "2시간 30분 이상 - 3시간 30분 미만 (편도 +10,000원 가산)",
            "3시간 30분 이상 (편도 +15,000원 가산)"
        ]
        
        def_idx2 = 2 if "3시간 30분 이상" in route_info2["duration"] else (1 if "2시간 30분 이상" in route_info2["duration"] else 0)
        dur2_choice = st.selectbox("오는 편 소요시간 가산", options=dur_options, index=def_idx2 if not is_manual2 else 0, disabled=not is_manual2, key=f"dur2_m_{dep2}_{dest2}")
        add2 = 15000 if "3시간 30분 이상" in dur2_choice else (10000 if "2시간 30분 이상" in dur2_choice else 0)
        actual_spent2 = fare2

    st.write("")
    total_actual_spent = st.number_input(
        "실제 교통비로 지출한 총 금액 (모든 영수증 합계, 원)",
        min_value=0,
        value=int(actual_spent1 + actual_spent2),
        step=100,
        key="total_actual_m_input"
    )
    
    total_x = (fare1 + add1) + (fare2 + add2)
    flight_bonus_total = (15000 if mode1 == "비행기 (항공편)" else 0) + (15000 if mode2 == "비행기 (항공편)" else 0)

# 실시간 계산 결과 산출
st.write("---")

# 1. 50,000원 초과 감액 규정 적용
is_capped = False
if total_x > 50000:
    calculated_amount = (total_x - 50000) / 2 + 50000
    is_capped = True
else:
    calculated_amount = total_x

# 2. 실제 지출액 상한선 검증 (항공 가산금이 산입된 경우 상한선 확장 적용)
max_allowed_cap = total_actual_spent + flight_bonus_total
final_refund = min(calculated_amount, max_allowed_cap)
is_actual_spent_limit = (calculated_amount > max_allowed_cap)

# 결과 출력
st.markdown("### 📊 실시간 계산 결과")
st.markdown(f"""
    <div class="result-box">
        <h4 style="margin:0; color:#0F52BA;">최종 환급 결정액</h4>
        <p style="font-size: 2.2rem; font-weight: bold; margin: 5px 0 0 0; color:#0A3D91;">
            {int(final_refund):,} 원
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("#### 🔍 세부 산출 과정")
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    **🛫 가는 편 기준액:**  
    * 이용 수단: {mode1}  
    * 기본 요금(기준액): {fare1:,.0f}원  
    * 추가 가산금: {add1:,}원  
    * **소계: {fare1 + add1:,.0f}원**
    """)
with col2:
    if trip_pattern in ["왕복 (동일 경로 왕복)", "가는 편과 오는 편의 경로/수단이 다름 (복합 여정)"]:
        st.markdown(f"""
        **🛬 오는 편 기준액:**  
        * 이용 수단: {mode2}  
        * 기본 요금(기준액): {fare2:,.0f}원  
        * 추가 가산금: {add2:,}원  
        * **소계: {fare2 + add2:,.0f}원**
        """)
    else:
        st.markdown("""
        **🛬 오는 편 기준액:**  
        * (편도 정산)
        """)

st.markdown(f"**규정 적용 전 기준 합계 ($X$):** **{total_x:,.0f}원**")

if is_capped:
    st.markdown(f"⚠️ **5만원 초과 감액 적용:** 기준액이 50,000원을 초과하여 공식 `(X - 50,000) / 2 + 50,000`이 적용되었습니다. → **{int(calculated_amount):,}원**")
else:
    st.markdown(f"✅ **5만원 이하 정상 적용:** 기준액이 50,000원 이하이므로 전액 인정됩니다. → **{int(calculated_amount):,}원**")

if flight_bonus_total > 0:
    st.info(f"✈️ **항공 가산금 혜택 반영:** 비행기 이용 추가금(+{flight_bonus_total:,}원)이 적용되었습니다.")

if is_actual_spent_limit:
    st.markdown(f"⚠️ **영수증 지출 한도 제한:** 계산 금액이 인정 상한선({max_allowed_cap:,}원)을 초과하여 최대 상한 금액까지만 환급 결정되었습니다.")
else:
    st.markdown("✅ **영수증 한도 검증 완료:** 계산된 환급액이 영수증 지출 승인 범위 내에 있어 전액 환급 가능합니다.")
