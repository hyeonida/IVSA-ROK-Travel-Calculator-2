import streamlit as st
import os

# 페이지 설정
st.set_page_config(
    page_title="IVSA 임원진 교통비 환급 계산기 (실시간 반응형)",
    page_icon="🏥",
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

st.title("🏥 IVSA 임원진 교통비 환급 계산기")
st.write("본인의 **출발지**와 **도착지**를 선택하면, 각 터미널별(서울경부, 동서울 등) 공식 우등고속버스 요금과 규정 소요시간이 자동으로 매핑되어 환급액을 실시간으로 계산해 줍니다.")

# 맵 이미지 표시 (존재하는 경우)
map_path = "ivsa_travel_map.png"
if os.path.exists(map_path):
    st.image(map_path, caption="IVSA 전국 수의과대학 공식 노선도 및 참고 요금 기준", use_container_width=True)
elif os.path.exists("/workspace/artifacts/ivsa_travel_map.png"):
    st.image("/workspace/artifacts/ivsa_travel_map.png", caption="IVSA 전국 수의과대학 공식 노선도 및 참고 요금 기준", use_container_width=True)

# 안내 문구 (접이식)
with st.expander("📌 IVSA 교통비 환급 핵심 규정 보기"):
    st.markdown("""
    * **기본 원칙:** 실제 이용 교통수단(KTX, 비행기 등)과 관계없이 **도시 간 우등 고속버스 요금**을 기준으로 지급합니다. [2]
    * **소요 시간 가산금 (편도당):**
        * 편도 소요 시간 **2시간 30분 이상**: 편도 요금 +10,000원 추가 [2]
        * 편도 소요 시간 **3시간 30분 이상**: 편도 요금 +15,000원 추가 [2]
        * **제주대생 항공편 이용 시**: 소요 시간 관계없이 편도 요금 +15,000원 추가 [2]
    * **5만원 초과 상한선 규정:** 
        * 환급 기준액($X$)이 50,000원을 초과할 경우, 초과 금액의 50%만 인정됩니다. 
        * **공식:** $(X - 50,000) / 2 + 50,000$ [2]
    * **실제 지출액 상한선:** 계산된 환급액이 아무리 높더라도, **실제로 지출한 금액(영수증 총합)을 초과할 수 없습니다.** [2, 3]
    """)

st.write("---")

# 위치 목록 정의
LOCATIONS = [
    "서울경부 / 서울센트럴 (행사장소)",
    "동서울 (행사장소)",
    "진주 (경상대)",
    "광주유스퀘어 (전남대)",
    "동대구터미널 (경북대)",
    "청주/세종 (충북대)",
    "유성/대전 (충남대)",
    "익산 (전북대)",
    "제주공항 (제주대)",
    "기타 (직접 입력)"
]

# 노선 데이터베이스 매트릭스 정의
# (출발지, 도착지) 쌍에 매핑되는 요금 및 시간 규정
ROUTES_DATABASE = {
    # 진주 <-> 서울경부
    ("진주 (경상대)", "서울경부 / 서울센트럴 (행사장소)"): {
        "fare": 34500,
        "duration": "3시간 30분 이상 (편도 +15,000원 가산)",
        "desc": "편도 소요시간 3시간 45분 적용 [3]"
    },
    # 진주 <-> 동서울
    ("진주 (경상대)", "동서울 (행사장소)"): {
        "fare": 34500,
        "duration": "3시간 30분 이상 (편도 +15,000원 가산)",
        "desc": "편도 소요시간 3시간 45분 적용 [3]"
    },
    # 광주 <-> 서울경부/센트럴
    ("광주유스퀘어 (전남대)", "서울경부 / 서울센트럴 (행사장소)"): {
        "fare": 33300,
        "duration": "3시간 30분 이상 (편도 +15,000원 가산)",
        "desc": "편도 소요시간 3시간 30분 적용 [3]"
    },
    # 광주 <-> 동서울
    ("광주유스퀘어 (전남대)", "동서울 (행사장소)"): {
        "fare": 33300,
        "duration": "3시간 30분 이상 (편도 +15,000원 가산)",
        "desc": "편도 소요시간 3시간 30분 적용 [1, 3]"
    },
    # 대구 <-> 서울경부
    ("동대구터미널 (경북대)", "서울경부 / 서울센트럴 (행사장소)"): {
        "fare": 36000,
        "duration": "3시간 30분 이상 (편도 +15,000원 가산)",
        "desc": "편도 소요시간 3시간 30분 적용 [1]"
    },
    # 대구 <-> 동서울
    ("동대구터미널 (경북대)", "동서울 (행사장소)"): {
        "fare": 36000,
        "duration": "3시간 30분 이상 (편도 +15,000원 가산)",
        "desc": "편도 소요시간 3시간 30분 적용 [1]"
    },
    # 청주/세종 <-> 서울경부
    ("청주/세종 (충북대)", "서울경부 / 서울센트럴 (행사장소)"): {
        "fare": 13300,
        "duration": "2시간 30분 미만 (추가금 없음)",
        "desc": "청주 ↔ 서울경부 13,300원 [1] / 세종 ↔ 서울경부 14,400원 [1] 기준 적용"
    },
    # 청주/세종 <-> 동서울
    ("청주/세종 (충북대)", "동서울 (행사장소)"): {
        "fare": 13300,
        "duration": "2시간 30분 미만 (추가금 없음)",
        "desc": "청주 ↔ 동서울 우등 요금 기준"
    },
    # 대전/유성 <-> 서울센트럴
    ("유성/대전 (충남대)", "서울경부 / 서울센트럴 (행사장소)"): {
        "fare": 16800,
        "duration": "2시간 30분 미만 (추가금 없음)",
        "desc": "유성 ↔ 서울센트럴 16,800원 ~ 16,900원 기준 적용 [1]"
    },
    # 대전/유성 <-> 동서울
    ("유성/대전 (충남대)", "동서울 (행사장소)"): {
        "fare": 16800,
        "duration": "2시간 30분 미만 (추가금 없음)",
        "desc": "유성 ↔ 동서울 우등 요금 기준"
    },
    # 익산 <-> 서울/용산
    ("익산 (전북대)", "서울경부 / 서울센트럴 (행사장소)"): {
        "fare": 13000,
        "duration": "2시간 30분 미만 (추가금 없음)",
        "desc": "익산 ↔ 서울 고속버스 우등 기준 적용 [1]"
    },
    # 익산 <-> 동서울
    ("익산 (전북대)", "동서울 (행사장소)"): {
        "fare": 13000,
        "duration": "2시간 30분 미만 (추가금 없음)",
        "desc": "익산 ↔ 동서울 고속버스 우등 기준 적용"
    }
}

# 양방향 데이터 검색 및 판정 헬퍼 함수
def lookup_route(dep, dest):
    if dep == dest:
        return {"fare": 0, "duration": "2시간 30분 미만 (추가금 없음)", "desc": "출발지와 도착지가 같습니다."}
    
    # 제주대 항공편 노선 여부
    if "제주공항" in dep or "제주공항" in dest:
        return {"fare": 0, "is_jeju": True, "duration": "제주대학교 학생 - 항공편 이용 (편도 +15,000원 가산)", "desc": "제주대 항공편 정산 대상 [1, 2]"}
    
    # 직접 입력 여부
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
    options=["왕복 (동일 경로 왕복)", "편도 (외길 여정)", "가는 편과 오는 편의 경로가 다름"],
    index=0,
    horizontal=True
)

st.write("")

# 실시간 변경을 위해 st.form을 걷어내고 컴포넌트를 직접 배치합니다!
is_jeju_trip = False

if trip_pattern == "왕복 (동일 경로 왕복)" or trip_pattern == "편도 (외길 여정)":
    st.subheader("📍 여정 경로 설정")
    col_dep, col_dest = st.columns(2)
    with col_dep:
        dep = st.selectbox("출발지 선택", options=LOCATIONS, index=2, key="dep_single")
    with col_dest:
        dest = st.selectbox("도착지 선택", options=LOCATIONS, index=0, key="dest_single")
        
    route_info = lookup_route(dep, dest)
    is_jeju_trip = route_info.get("is_jeju", False)
    is_manual = route_info.get("is_manual", False)
    
    st.caption(f"💡 **선택 경로 정보:** {route_info['desc']}")
    
    if is_jeju_trip:
        st.subheader("✈️ 제주대 항공편 정산 정보")
        flight_fare = st.number_input(
            "실제 비행기표 결제 총 금액 (왕복/편도 전체 결제액, 원)",
            min_value=0,
            value=120000 if trip_pattern == "왕복 (동일 경로 왕복)" else 60000,
            step=1000,
            key="flight_single"
        )
    else:
        st.subheader("🚌 버스 요금 및 가산 요건")
        fare1 = st.number_input(
            "편도당 우등 버스 요금 (원)",
            min_value=0,
            value=route_info["fare"] if not is_manual else 13300,
            step=100,
            disabled=not is_manual,
            key="fare_single"
        )
        
        dur_options = [
            "2시간 30분 미만 (추가금 없음)",
            "2시간 30분 이상 ~ 3시간 30분 미만 (편도 +10,000원 가산)",
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
            key="dur_single"
        )
        
        # 왕복 여부
        is_round = trip_pattern == "왕복 (동일 경로 왕복)"
        
        actual_spent = st.number_input(
            "실제 교통비로 지출한 총 금액 (영수증 총합, 원)",
            min_value=0,
            value=int(fare1 * 2) if is_round else int(fare1),
            step=100,
            key="actual_single"
        )
        
else: # 가는 편과 오는 편의 경로가 다름
    st.subheader("🛫 가는 편 경로 (Outbound)")
    col_dep1, col_dest1 = st.columns(2)
    with col_dep1:
        dep1 = st.selectbox("출발지 선택", options=LOCATIONS, index=2, key="dep_g1")
    with col_dest1:
        dest1 = st.selectbox("도착지 선택", options=LOCATIONS, index=0, key="dest_g1")
        
    route_info1 = lookup_route(dep1, dest1)
    is_jeju1 = route_info1.get("is_jeju", False)
    is_manual1 = route_info1.get("is_manual", False)
    
    st.caption(f"가는 편 경로 정보: {route_info1['desc']}")
    
    st.write("---")
    st.subheader("🛬 오는 편 경로 (Inbound)")
    col_dep2, col_dest2 = st.columns(2)
    with col_dep2:
        dep2 = st.selectbox("출발지 선택", options=LOCATIONS, index=0, key="dep_g2")
    with col_dest2:
        dest2 = st.selectbox("도착지 선택", options=LOCATIONS, index=2, key="dest_g2")
        
    route_info2 = lookup_route(dep2, dest2)
    is_jeju2 = route_info2.get("is_jeju", False)
    is_manual2 = route_info2.get("is_manual", False)
    
    st.caption(f"오는 편 경로 정보: {route_info2['desc']}")
    
    is_jeju_trip = is_jeju1 or is_jeju2
    
    if is_jeju_trip:
        st.subheader("✈️ 제주대 항공편 정산 정보")
        flight_fare = st.number_input(
            "실제 비행기표 결제 총 금액 (전체 결제액, 원)",
            min_value=0,
            value=120000,
            step=1000,
            key="flight_multi"
        )
    else:
        st.subheader("🚌 버스 요금 및 가산 요건")
        col_fare1, col_fare2 = st.columns(2)
        with col_fare1:
            fare1 = st.number_input(
                "가는 편 버스 요금 (원)",
                min_value=0,
                value=route_info1["fare"] if not is_manual1 else 13300,
                step=100,
                disabled=not is_manual1,
                key="fare_g1"
            )
        with col_fare2:
            fare2 = st.number_input(
                "오는 편 버스 요금 (원)",
                min_value=0,
                value=route_info2["fare"] if not is_manual2 else 13300,
                step=100,
                disabled=not is_manual2,
                key="fare_g2"
            )
            
        dur_options = [
            "2시간 30분 미만 (추가금 없음)",
            "2시간 30분 이상 ~ 3시간 30분 미만 (편도 +10,000원 가산)",
            "3시간 30분 이상 (편도 +15,000원 가산)"
        ]
        
        default_dur_idx1 = 0
        if "3시간 30분 이상" in route_info1["duration"]:
            default_dur_idx1 = 2
        elif "2시간 30분 이상" in route_info1["duration"]:
            default_dur_idx1 = 1
            
        default_dur_idx2 = 0
        if "3시간 30분 이상" in route_info2["duration"]:
            default_dur_idx2 = 2
        elif "2시간 30분 이상" in route_info2["duration"]:
            default_dur_idx2 = 1
            
        col_dur1, col_dur2 = st.columns(2)
        with col_dur1:
            duration_choice1 = st.selectbox(
                "가는 편 소요 시간 기준",
                options=dur_options,
                index=default_dur_idx1 if not is_manual1 else 0,
                disabled=not is_manual1,
                key="dur_g1"
            )
        with col_dur2:
            duration_choice2 = st.selectbox(
                "오는 편 소요 시간 기준",
                options=dur_options,
                index=default_dur_idx2 if not is_manual2 else 0,
                disabled=not is_manual2,
                key="dur_g2"
            )
            
        actual_spent = st.number_input(
            "실제 교통비로 지출한 총 금액 (영수증 총합, 원)",
            min_value=0,
            value=int(fare1 + fare2),
            step=100,
            key="actual_multi"
        )

# 실시간 즉시 계산을 적용하여 버튼 없이도 금액을 바로 보여줍니다!
st.write("---")

if is_jeju_trip:
    # 제주대 항공 환급액 로직
    is_round_trip = True
    if trip_pattern == "편도 (외길 여정)":
        is_round_trip = False
        
    extra_fee = 30000 if is_round_trip else 15000
    total_x = flight_fare + extra_fee
    
    is_capped = False
    if total_x > 50000:
        calculated_amount = (total_x - 50000) / 2 + 50000
        is_capped = True
    else:
        calculated_amount = total_x
        
    final_refund = min(calculated_amount, flight_fare)
    is_actual_spent_limit = calculated_amount > flight_fare
    
    # 결과 카드 출력
    st.markdown("### 📊 실시간 계산 결과")
    st.markdown(f"""
        <div class="result-box">
            <h4 style="margin:0; color:#0F52BA;">최종 환급 결정액 (제주대 항공편 전용)</h4>
            <p style="font-size: 2.2rem; font-weight: bold; margin: 5px 0 0 0; color:#0A3D91;">
                {int(final_refund):,} 원
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 🔍 세부 산출 과정")
    st.markdown(f"""
    * **✈️ 실제 비행기 요금 (기준액):** {flight_fare:,}원
    * **🎁 제주대 항공 가산금:** {extra_fee:,}원 ({"왕복" if is_round_trip else "편도"} 적용)
    * **규정 적용 전 기준 합계 ($X$):** **{total_x:,}원**
    """)
    
    if is_capped:
        st.markdown(f"⚠️ **5만원 초과 감액 적용:** 기준액이 50,000원을 초과하여 공식 `(X - 50,000) / 2 + 50,000`이 적용되었습니다. → **{int(calculated_amount):,}원**")
    else:
        st.markdown(f"✅ **5만원 이하 정상 적용:** 기준액이 50,000원 이하이므로 전액 인정됩니다. → **{int(calculated_amount):,}원**")
        
    if is_actual_spent_limit:
        st.markdown(f"⚠️ **영수증 지출 한도 제한:** 계산된 환급액이 비행기표 실제 결제 금액({flight_fare:,}원)보다 크므로, 실제 지출금액 한도 내에서 환급됩니다.")
        
else:
    # 일반 버스 노선 정산 로직
    if trip_pattern == "왕복 (동일 경로 왕복)" or trip_pattern == "편도 (외길 여정)":
        add1 = 0
        if "3시간 30분 이상" in duration_choice:
            add1 = 15000
        elif "2시간 30분 이상" in duration_choice:
            add1 = 10000
            
        is_round = trip_pattern == "왕복 (동일 경로 왕복)"
        
        # 기준액 계산
        if is_round:
            total_x = (fare1 + add1) * 2
        else:
            total_x = fare1 + add1
            
        total1 = fare1 + add1
        total2 = fare1 + add1 if is_round else 0
        add2 = add1 if is_round else 0
        fare2 = fare1 if is_round else 0
    else:
        add1 = 0
        if "3시간 30분 이상" in duration_choice1:
            add1 = 15000
        elif "2시간 30분 이상" in duration_choice1:
            add1 = 10000
            
        add2 = 0
        if "3시간 30분 이상" in duration_choice2:
            add2 = 15000
        elif "2시간 30분 이상" in duration_choice2:
            add2 = 10000
            
        total1 = fare1 + add1
        total2 = fare2 + add2
        total_x = total1 + total2
        
    # 5만원 초과 규정 적용
    is_capped = False
    if total_x > 50000:
        calculated_amount = (total_x - 50000) / 2 + 50000
        is_capped = True
    else:
        calculated_amount = total_x
        
    # 실제 지출액 상한선 적용
    final_refund = min(calculated_amount, actual_spent)
    is_actual_spent_limit = calculated_amount > actual_spent
    
    # 결과 카드 출력
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
        * 기본 요금: {fare1:,}원  
        * 추가 가산금: {add1:,}원  
        * **소계: {total1:,}원**
        """)
    with col2:
        if trip_pattern == "왕복 (동일 경로 왕복)" or trip_pattern == "가는 편과 오는 편의 경로가 다름":
            st.markdown(f"""
            **🛬 오는 편 기준액:**  
            * 기본 요금: {fare2:,}원  
            * 추가 가산금: {add2:,}원  
            * **소계: {total2:,}원**
            """)
        else:
            st.markdown("""
            **🛬 오는 편 기준액:**  
            * (편도 정산이므로 기록 없음)
            """)
            
    st.markdown(f"**규정 적용 전 기준 합계 ($X$):** {total_x:,}원")
    
    if is_capped:
        st.markdown(f"⚠️ **5만원 초과 감액 적용:** 기준액이 50,000원을 초과하여 공식 `(X - 50,000) / 2 + 50,000`이 적용되었습니다. → **{int(calculated_amount):,}원**")
    else:
        st.markdown(f"✅ **5만원 이하 정상 적용:** 기준액이 50,000원 이하이므로 전액 인정됩니다. → **{int(calculated_amount):,}원**")
        
    if is_actual_spent_limit:
        st.markdown(f"⚠️ **영수증 지출 한도 제한:** 계산된 환급액이 실제 지출한 금액({actual_spent:,}원)보다 크므로, 실제 영수증 지출 금액까지만 환급됩니다.")
    else:
        st.markdown("✅ **영수증 한도 검증 완료:** 계산된 환급액이 실제 영수증 범위 내에 있으므로 전액 환급이 가능합니다.")
        
    st.info("💡 계산된 환급 금액은 규정 기준을 엄격하게 적용한 금액이며, 최종 지급을 위해서는 제출하신 버스 기준 요금 캡처 및 영수증 증빙이 일치해야 합니다.")
