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

# Couchbase 연결
def get_couchbase_connection():
    cluster = Cluster(
        'couchbase://localhost:11210',
        ClusterOptions(
            PasswordAuthenticator('Administrator', YOUR_PASSWORD)
        )
    )
    bucket = cluster.bucket('recipes')
    collection = bucket.default_collection()
    return cluster, collection

# Couchbase FTS 검색 함수
def search_recipe(query):
    cluster, collection = get_couchbase_connection()
    
    try:
        # 기본 Match 쿼리 생성
        search_query = MatchQuery(query)
        
        # 검색 실행
        search_result = cluster.search_query(
            "recipes._default.recipe-index",  # 인덱스 이름
            search_query,
            limit=10
        )
        
        hits = []
        # 검색 결과 처리
        for hit in search_result:
            try:
                # 문서 ID로 실제 문서 가져오기
                doc = collection.get(hit.id).content_as[dict]
                hits.append({
                    "_source": {
                        "RecipeName": doc.get("name", ""),
                        "Image": doc.get("img", ""),
                        "Ingredients_pre": doc.get("ingredients", []),
                        "Steps": doc.get("recipe_steps", {}),
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

# ingredients 전처리 함수
def process_type1(data):
    return data.replace('\n', '').replace('dd', '').strip()

# JSON 문자열 정리 함수
def clean_json_string(json_string):
    return re.sub(r'[\x00-\x1F\x7F]', '', json_string)

# 이미지 URL 수정 함수
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
    st.write("""# 👩‍🍳키워드 입력을 통한 레시피 찾기""")
    st.write(' ')
    st.write(' ')
    # 사용자로부터 재료 입력 받기
    ingredients_input = st.text_input("음식, 재료 등 레시피 키워드를 입력하세요")

    # 사용자가 재료를 입력한 경우
    if ingredients_input:
        # Couchbase FTS로 레시피 검색
        results = search_recipe(ingredients_input)
        
        # 검색 결과가 있을 경우
        if results:
            st.header("검색 결과")
            recipe_names = [hit['_source']['RecipeName'] for hit in results]
            selected_recipe = st.selectbox("검색된 레시피 선택", recipe_names)
            
            # 선택한 레시피 정보 표시
            for hit in results:
                if hit['_source']['RecipeName'] == selected_recipe:
                    st.subheader("선택한 레시피")
                    image_url = fix_image_url(hit['_source']['Image'])
                    if image_url:
                        st.image(image_url, width=250, use_column_width='auto')
                    
                    st.write("### 요리명")
                    st.write(f"{hit['_source']['RecipeName']}")
                    steps = hit['_source'].get('Steps', {}).get('txt', '')
                    
                    try:
                        ingredients_list = hit['_source']['Ingredients_pre']
                        if isinstance(ingredients_list, str):
                            ingredients_list = json.loads(ingredients_list)
                        ingredient_names = ', '.join([ingredient.get('ingre_name', '') 
                                                   for ingredient in ingredients_list])
                    except (ValueError, SyntaxError, json.JSONDecodeError):
                        ingredient_names = process_type1(str(hit['_source']['Ingredients_pre']))
                    
                    st.write("### 재료")
                    st.write(f"{ingredient_names}")
                    st.write("### 조리법")
                    
                    if isinstance(steps, str):
                        lines = steps.strip().split("\n")
                        processed_steps = ""
                        for line in lines:
                            parts = line.split(", ")
                            for part in parts:
                                if not part.startswith("http"):
                                    st.write(part)
                                    processed_steps += part + "\n"
                    
                    st.markdown("---")

                    content = {
                        "title": hit['_source']['RecipeName'],
                        "ingredients": ingredient_names,
                        "steps": processed_steps
                    }
                    
                    if st.button("✅다이어트 레시피 변환", key=f"select_diet"):
                        st.session_state.diet_recipe_output = diet_recipe(content)
                        if st.session_state.diet_recipe_output:
                            selected_output = st.session_state.diet_recipe_output
                            clean_selected_output = clean_json_string(selected_output)
                            try:
                                output_json = json.loads(clean_selected_output)
                            except json.JSONDecodeError as e:
                                st.error(f"JSON 파싱 오류: {e}")
                                return

                            if output_json:
                                st.write("### 🍱요리명")
                                st.write(output_json.get('title', 'Title not available'))
                                
                                st.write("### 🥬재료")
                                st.write('✅' + output_json.get('ingredients', 'Ingredients not available'))
                                
                                st.write("### 👨🏻‍🍳조리법")
                                st.write('✅' + output_json.get('steps', 'Steps not available'))
                            else:
                                st.write("검색 결과가 없습니다.")
        else:
            st.write("검색 결과가 없습니다.")

if __name__ == "__main__":
    recipe_engine()
