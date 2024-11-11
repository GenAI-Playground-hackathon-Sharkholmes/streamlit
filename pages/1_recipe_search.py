import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import ast
import json
import re
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.search import (
    SearchQuery,
    MatchQuery,
    ConjunctionQuery,
    DisjunctionQuery
)
from recipe_create import diet_recipe
import backend as be  


# 세션 상태 초기화
if 'memory' not in st.session_state:
    st.session_state.memory = be.buff_memory()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Couchbase 연결
def get_couchbase_connection():
    cluster = Cluster(
        'couchbase://HOST',
        ClusterOptions(
            PasswordAuthenticator('Administrator', 'PASSWORD')
        )
    )
    bucket = cluster.bucket('recipes')
    collection = bucket.default_collection()
    return cluster, collection

# Couchbase FTS 검색 함수
def search_recipe(query):
    cluster, collection = get_couchbase_connection()
    
    try:
        search_query = MatchQuery(query)
        search_result = cluster.search_query(
            "recipes._default.recipe-index",
            search_query,
            limit=10
        )
        
        hits = []
        for hit in search_result:
            try:
                doc = collection.get(hit.id).content_as[dict]
                # info1 필드 처리하여 단계별 텍스트와 이미지 URL 매칭
                steps_with_images = []
                if isinstance(doc.get("info1"), str):
                    items = [item.strip() for item in doc["info1"].split(",")]
                    current_step = ""
                    
                    for item in items:
                        if item.startswith("http"):
                            # 현재 단계에 이미지 URL 추가
                            if current_step:
                                steps_with_images.append({
                                    "text": current_step,
                                    "image": fix_image_url(item)
                                })
                                current_step = ""
                        else:
                            # 텍스트 단계 저장
                            if item.strip():
                                if current_step:  # 이전 단계가 이미지 없이 끝난 경우
                                    steps_with_images.append({
                                        "text": current_step,
                                        "image": None
                                    })
                                current_step = item
                    
                    # 마지막 단계 처리
                    if current_step:
                        steps_with_images.append({
                            "text": current_step,
                            "image": None
                        })
                
                hits.append({
                    "_source": {
                        "RecipeName": doc.get("name", ""),
                        "Image": doc.get("img", ""),
                        "Ingredients_pre": doc.get("ingredients", []),
                        "Steps": steps_with_images,
                        "Summary": doc.get("summary", "")
                    }
                })
            except Exception as e:
                st.error(f"문서 가져오기 오류: {str(e)}")
                continue
                
        return hits
    except Exception as e:
        st.error(f"검색 중 오류가 발생했습니다: {str(e)}")
        return []

def process_type1(data):
    return data.replace('\n', '').replace('dd', '').strip()

def clean_json_string(json_string):
    return re.sub(r'[\x00-\x1F\x7F]', '', json_string)

def fix_image_url(url):
    if not url:
        return url
    if not url.startswith("http"):
        url = "https://" + url
    if url.startswith("https //"):
        parts = url.split(" ", 1)
        url = parts[0] + ":" + parts[1]
    return url

def recipe_engine():
    st.write(' ')
    
    # content 초기화
    content = None
    
    
    ingredients_input = st.text_input("음식, 재료 키워드를 입력하여 레시피를 찾아보세요")

    if ingredients_input:
        results = search_recipe(ingredients_input)
        
        if results:
            st.header("검색 결과")
            recipe_names = [hit['_source']['RecipeName'] for hit in results]
            selected_recipe = st.selectbox("검색된 레시피 선택", recipe_names)
            
            for hit in results:
                if hit['_source']['RecipeName'] == selected_recipe:
                    st.subheader("선택한 레시피")
                    image_url = fix_image_url(hit['_source']['Image'])
                    if image_url:
                        st.image(image_url, width=250, use_column_width='auto')
                    
                    st.write("### 요리명")
                    st.write(f"{hit['_source']['RecipeName']}")
                    
                    try:
                        ingredients_list = hit['_source']['Ingredients_pre']
                        if isinstance(ingredients_list, str):
                            # 쉼표로 구분된 재료 목록 처리
                            ingredients = [ing.strip() for ing in ingredients_list.split()]
                            ingredient_names = ', '.join(ingredients)
                        else:
                            ingredient_names = process_type1(str(ingredients_list))
                    except (ValueError, SyntaxError, json.JSONDecodeError):
                        ingredient_names = process_type1(str(hit['_source']['Ingredients_pre']))
                    
                    st.write("### 재료")
                    st.write(f"{ingredient_names}")
                    
                    st.write("### 조리법")
                    steps = hit['_source']['Steps']
                    for i, step in enumerate(steps, 1):
                        # 단계별 설명
                        st.write(f"{i}. {step['text']}")
                        # 단계별 이미지가 있으면 표시
                        if step['image']:
                            try:
                                st.image(step['image'], width=400, use_column_width='auto')
                            except Exception as e:
                                st.error(f"이미지 로딩 오류: {str(e)}")
                    
                    st.markdown("---")

                    # 조리 단계 텍스트만 추출하여 저장
                  
                    # 조리 단계 텍스트만 추출하여 저장
                    steps_text = "\n".join([f"{i+1}. {step['text']}" for i, step in enumerate(steps)])
                    
                    # diet_recipe 사용하여 선택한 레시피 내용을 세션에 저장
                    content = {
                        "title": hit['_source']['RecipeName'],
                        "ingredients": ingredient_names,
                        "steps": steps_text
                    }
                    st.session_state.selected_output = diet_recipe(content)
        
        else:
            st.write("검색 결과가 없습니다.")
    return content




# UI 구성
st.title("Recipe Search")
content = recipe_engine()

# 채팅 UI
for message in st.session_state.chat_history:
    with st.chat_message(message['role']):
        st.markdown(message["text"])

input_text = st.chat_input("질문을 입력하세요")
if input_text:
    with st.chat_message("나"):
        st.markdown(input_text)
        
    prompt = "우리는 지금 기존 레시피에서 재료를 변경하고 있어. 최대한 재료를 바꾸려고 노력을 해야해."
    
    # 기존 레시피 내용을 JSON 문자열로 변환
    recipe_text = json.dumps(st.session_state.selected_output, ensure_ascii=False)
    
    # 사용자 입력과 기존 레시피 내용을 결합하여 input_text로 사용
    combined_input = f"{prompt}\n레시피 정보: {recipe_text}\n사용자 요청: {input_text}"
    
    st.session_state.chat_history.append({"role": "user", "text": combined_input})
    
    # 대화 생성
    if st.session_state.selected_output:
        chat_response = be.cvs_chain(input_text=combined_input, memory=st.session_state.memory)
        
        with st.chat_message("챗봇"):
            st.markdown(chat_response)
        
        st.session_state.chat_history.append({"role": "assistant", "text": chat_response})