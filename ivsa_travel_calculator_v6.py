import streamlit as st
import os

# 페이지 설정
st.set_page_config(
    page_title="IVSA ROK 임원진 교통비 환급 계산기 (통합 지도 노선도형)",
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

st.title("🏥 IVSA ROK 임원진 교통비 환급 계산기")
st.write("본인의 소속 대학교를 선택하시면 규정에 따른 공식 요금과 환급액이 자동으로 산출됩니다.")

# --- 1. 지도 모식도 (Visual Map Schematic) 표시 ---
st.subheader("🗺️ IVSA ROK 전국 수의과대학 교통비 기준 노선도")

# 로컬(배포 환경)에 지도 이미지가 존재하는지 확인 후 출력
map_filename = "ivsa_travel_map.png"
if os.path.exists(map_filename):
    st.image(map_filename, caption="IVSA ROK 전국 수의과대학 ↔ 서울 교통 노선 모식도 (우등 버스 기준 운임)", use_container_width=True)
else:
    # 깃허브 업로드 전일 경우를 대비해, 다운로드 가이드와 안내 문구를 제공합니다.
    st.info("💡 **알림:** 깃허브 저장소에 `ivsa_travel_map.png` 파일을 업로드하시면 여기에 멋진 인터랙티브 지도 모식도가 나타납니다!")
    st.warning("현재 지도 파일이 저장소에 없지만, 계산기 기능은 아래에서 정상적으로 작동합니다. 😊")

st.write("---")

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

# 학교 데이터베이스 정의
UNIV_DATABASE = {
    "경상대학교 (진주 ↔ 서울)": {
        "fare": 34500,
        "duration": "3시간 30분 이상 (편도 +15,000원 가산)",
        "desc": "편도 소요시간 3시간 45분 적용 [3]"
    },
    "전남대학교 (광주 ↔ 서울)": {
        "fare": 33300,
        "duration": "3시간 30분 이상 (편도 +15,000원 가산)",
        "desc": "편도 소요시간 3시간 30분 적용 [3]"
    },
    "경북대학교 (대구 ↔ 서울)": {
        "fare": 36000,
        "duration": "3시간 30분 이상 (편도 +15,000원 가산)",
        "desc": "편도 소요시간 3시간 30분 적용 [1]"
    },
    "충북대학교 (청주 ↔ 서울)": {
        "fare": 13300,
        "duration": "2시간 30분 미만 (추가금 없음)",
        "desc": "편도 소요시간 1시간 30분 적용 [1, 3]"
    },
    "충남대학교 (대전/유성 ↔ 서울)": {
        "fare": 16800,
        "duration": "2시간 30분 미만 (추가금 없음)",
        "desc": "편도 소요시간 2시간 내외 적용 [1]"
    },
    "전북대학교 (익산 ↔ 서울)": {
        "fare": 17500, # 대략적인 우등 버스 환산 요금
        "duration": "2시간 30분 미만 (추가금 없음)",
        "desc": "편도 소요시간 2시간 내외 적용 [1]"
    },
    "제주대학교 (항공편 이용)": {
        "fare": 0,
        "duration": "제주대학교 학생 - 항공편 이용 (편도 +15,000원 가산)",
        "desc": "항공 가산금 자동 적용 [2]"
    },
    "직접 입력 (위 목록에 없거나 다른 경로)": {
        "fare": 0,
        "duration": "직접 선택",
        "desc": "요금과 소요시간을 직접 기입합니다."
    }
}

# 1. 소속 대학 선택
selected_univ = st.selectbox(
    "🏫 본인의 소속 수의과대학(또는 노선)을 선택해 주세요",
    options=list(UNIV_DATABASE.keys()),
    index=0
)

# 선택된 대학 정보 추출
univ_info = UNIV_DATABASE[selected_univ]
st.info(f"💡 **노선 가이드:** {univ_info['desc']}")

st.write("")

# 폼 생성
if "제주대학교" in selected_univ:
    # 제주대 전용 폼
    with st.form("jeju_calculator_form"):
        st.subheader("✈️ 제주대학교 학생 항공편 정산")
        st.write("제주대 임원은 규정에 따라 실제 비행기표 구매 금액을 기준으로 정산하며, 편도당 15,000원의 항공 이용 가산금이 추가됩니다. [1, 2]")
        
        trip_type = st.radio(
            "여정 종류를 선택하세요",
            options=["왕복 (Round Trip)", "편도 (One Way)"],
            index=0,
            horizontal=True,
            key="jeju_trip"
        )
        
        flight_fare = st.number_input(
            "실제 비행기표 결제 총 금액 (영수증 합계, 원)",
            min_value=0,
            value=120000,
            step=1000,
            key="jeju_flight_fare"
        )
        
        submitted_jeju = st.form_submit_button("💰 제주대 환급 금액 계산하기")

    if submitted_jeju:
        extra_fee = 30000 if "왕복" in trip_type else 15000
        total_x = flight_fare + extra_fee
        
        is_capped = False
        if total_x > 50000:
            calculated_amount = (total_x - 50000) / 2 + 50000
            is_capped = True
        else:
            calculated_amount = total_x
            
        final_refund = min(calculated_amount, flight_fare)
        is_actual_spent_limit = calculated_amount > flight_fare
        
        # 결과 화면 출력
        st.markdown("### 📊 계산 결과")
        st.markdown(f"""
            <div class="result-box">
                <h4 style="margin:0; color:#0F52BA;">최종 환급 결정액 (제주대 항공편 전용)</h4>
                <p style="font-size: 2rem; font-weight: bold; margin: 5px 0 0 0; color:#0A3D91;">
                    {int(final_refund):,} 원
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🔍 세부 산출 과정")
        st.markdown(f"""
        * **✈️ 비행기 요금 (기본 기준액):** {flight_fare:,}원
        * **🎁 제주대 항공 가산금:** {extra_fee:,}원 ({trip_type} 적용)
        * **규정 적용 전 기준 합계 ($X$):** **{total_x:,}원**
        """)
        
        if is_capped:
            st.markdown(f"⚠️ **5만원 초과 감액 적용:** 기준액이 50,000원을 초과하여 공식 `(X - 50,000) / 2 + 50,000`이 적용되었습니다. → **{int(calculated_amount):,}원**")
        else:
            st.markdown(f"✅ **5만원 이하 정상 적용:** 기준액이 50,000원 이하이므로 전액 인정됩니다. → **{int(calculated_amount):,}원**")

        if is_actual_spent_limit:
            st.markdown(f"⚠️ **영수증 지출 한도 제한:** 계산된 환급액이 비행기표 결제 금액({flight_fare:,}원)보다 크므로, 실제 지출 금액까지만 환급됩니다.")
        
        st.info("💡 제주대학교 학생은 비행기 탑승권과 영수증 증빙을 모두 업로드해야 정상 환급 처리가 완료됩니다.")

else:
    # 육지 대학용 폼
    is_manual = "직접 입력" in selected_univ
    
    with st.form("main_calculator_form"):
        st.subheader("🛫 가는 편 (Outbound)")
        fare1 = st.number_input(
            "가는 편 우등 고속버스 요금 (원)", 
            min_value=0, 
            value=univ_info["fare"] if not is_manual else 13300, 
            step=100, 
            key="fare1",
            disabled=not is_manual
        )
        
        dur1_options = [
            "2시간 30분 미만 (추가금 없음)",
            "2시간 30분 이상 ~ 3시간 30분 미만 (편도 +10,000원 가산)",
            "3시간 30분 이상 (편도 +15,000원 가산)"
        ]
        default_dur_idx1 = 0
        if "3시간 30분 이상" in univ_info["duration"]:
            default_dur_idx1 = 2
        elif "2시간 30분 이상" in univ_info["duration"]:
            default_dur_idx1 = 1
            
        duration_choice1 = st.selectbox(
            "가는 편 소요 시간 선택",
            options=dur1_options,
            index=default_dur_idx1 if not is_manual else 0,
            key="dur1",
            disabled=not is_manual
        )

        st.write("")
        st.subheader("🛬 오는 편 (Inbound)")
        fare2 = st.number_input(
            "오는 편 우등 고속버스 요금 (원)", 
            min_value=0, 
            value=univ_info["fare"] if not is_manual else 13300, 
            step=100, 
            key="fare2",
            disabled=not is_manual
        )
        
        duration_choice2 = st.selectbox(
            "오는 편 소요 시간 선택",
            options=dur1_options,
            index=default_dur_idx1 if not is_manual else 0,
            key="dur2",
            disabled=not is_manual
        )

        st.write("")
        st.subheader("🧾 증빙 및 실제 영수증 총액")
        actual_spent = st.number_input(
            "실제 교통비로 지출한 총 금액 (모든 영수증의 합계, 원)", 
            min_value=0, 
            value=int(fare1 + fare2) if fare1 + fare2 > 0 else 30000, 
            step=100, 
            key="actual"
        )

        # 제출 버튼
        submitted = st.form_submit_button("💰 환급 금액 계산하기")

    if submitted:
        # 1. 가는 편 가산금 판정
        add1 = 0
        if "3시간 30분 이상" in duration_choice1:
            add1 = 15000
        elif "2시간 30분 이상" in duration_choice1:
            add1 = 10000
        total1 = fare1 + add1

        # 2. 오는 편 가산금 판정
        add2 = 0
        if "3시간 30분 이상" in duration_choice2:
            add2 = 15000
        elif "2시간 30분 이상" in duration_choice2:
            add2 = 10000
        total2 = fare2 + add2

        # 3. 총 기준액(X) 산출
        total_x = total1 + total2

        # 4. 50,000원 초과 규정 적용
        is_capped = False
        if total_x > 50000:
            calculated_amount = (total_x - 50000) / 2 + 50000
            is_capped = True
        else:
            calculated_amount = total_x

        # 5. 실제 지불액 상한선 적용
        final_refund = min(calculated_amount, actual_spent)
        is_actual_spent_limit = calculated_amount > actual_spent

        # 결과 화면 출력
        st.markdown("### 📊 계산 결과")
        
        st.markdown(f"""
            <div class="result-box">
                <h4 style="margin:0; color:#0F52BA;">최종 환급 결정액</h4>
                <p style="font-size: 2rem; font-weight: bold; margin: 5px 0 0 0; color:#0A3D91;">
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
            * 추가 가산금: {add1:,}원  \n            * **소계: {total1:,}원**
            """)
        with col2:
            st.markdown(f"""
            **🛬 오는 편 기준액:**  \n            * 기본 요금: {fare2:,}원  
            * 추가 가산금: {add2:,}원  \n            * **소계: {total2:,}원**
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
