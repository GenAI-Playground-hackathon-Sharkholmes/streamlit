import streamlit as st
from openai import OpenAI

# 사이드바 설정
with st.sidebar:
    st.markdown("## 🍳 AI 요리 도우미")
    st.markdown("**재료 기반 추천**")
    if st.button("안성재 Mode"):
        st.session_state["mode"] = "ansungjae"
    st.markdown("**재료 대체 추천**")
    if st.button("백종원 Mode"):
        st.session_state["mode"] = "baekjongwon"

    st.markdown("## 🗂 채팅 히스토리")
    st.button("채팅 히스토리 보기", key="chat_history")

    st.markdown("## 🔎 검색엔진")
    st.button("레시피 검색하기", key="search_recipes")

    st.markdown("## 🛒 제품 추천")
    st.image("https://via.placeholder.com/150", caption="동원 참치")
    if st.button("동원 참치 구매하기"):
        st.write("[쿠팡 링크로 이동](https://www.coupang.com/)")

# 챗봇 메인 페이지 설정
st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# 이전 대화 표시
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 사용자 입력 처리
if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # ChatGPT 응답 생성
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state["messages"])
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

# 레시피 이미지 생성 버튼 추가
if st.button("레시피 이미지 생성"):
    st.write("레시피 이미지 생성 중...")