import streamlit as st

st.title("오늘의 의도를 살리고 싶은 재료")
ingredients = st.text_input("냉장고 속 주요 재료를 입력하세요")

if st.button("추천 받기"):
    st.experimental_set_query_params(page="chatbot")   
    st.write("추천 받은 레시피를 확인하려면, Chatbot 페이지로 이동하세요.")