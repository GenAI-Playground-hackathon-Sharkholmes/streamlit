import streamlit as st

# CSS 파일
# with open("style/style.css") as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
# 로고 이미지 
st.image("img/logo.png", use_column_width=True)

if "mode" not in st.session_state:
    st.session_state.mode = "main"  # 기본 페이지 main

# 두 가지 모드 - 안성재 모드 / 백종원 모드
col1, col2 = st.columns(2)

with col1:
    st.image("img/Ahn-Chef.png", caption="안성재 모드", use_column_width=True)
    st.markdown(
        """
        <div style="text-align: center;">
            <h4>재료 기반 요리 추천</h4>
            <p>가지고 있는 재료로 요리 레시피를 추천해드립니다.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.image("img/Baek-Chef.png", caption="백종원 모드", use_column_width=True)
    st.markdown(
        """
        <div style="text-align: center;">
            <h4>재료 대체 추천</h4>
            <p>없는 재료를 다른 재료로 대체하는 방법을 알려드립니다.</p>
        </div>
        """,
        unsafe_allow_html=True
    )