from pathlib import Path
import streamlit as st
import pandas as pd
import json
import re
from PIL import Image
from io import BytesIO
import os
from recipe_create import (
    diet_recipe,
    effect_create,
    extract_text,
    modify_recipe,
    generate_recipe_image
)

def clean_json_string(json_string):
    """JSON 문자열 정제"""
    return re.sub(r'[\x00-\x1F\x7F]', '', json_string)

def display_generated_image(image_bytes):
    """
    Streamlit에서 생성된 이미지를 표시
    
    Args:
        image_bytes (bytes): 이미지 바이트 데이터
    """
    if image_bytes:
        try:
            image = Image.open(BytesIO(image_bytes))
            st.image(image, caption="생성된 레시피 이미지", use_column_width=True)
        except Exception as e:
            st.error(f"이미지 표시 실패: {str(e)}")

# 세션 상태 초기화
if 'selected_output' not in st.session_state:
    st.session_state.selected_output = None
if 'selected_recipe' not in st.session_state:
    st.session_state.selected_recipe = None
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'modified_recipe' not in st.session_state:
    st.session_state.modified_recipe = None
if 'current_image' not in st.session_state:
    st.session_state.current_image = None

def load_data():
    """데이터 로드"""
    try:
        youtube_df = pd.read_csv('./data/Youtube_search_df.csv')
        results = []
        for _, row in youtube_df.iterrows():
            results.append({
                'type': 'youtube',
                'title': row['title'],
                'link': row['url'],
                'view': row['view'],
                'upload_date': row['upload_date']
            })
        return results
    except Exception as e:
        st.error(f"데이터 로드 실패: {str(e)}")
        return []

def display_recipes(results):
    """레시피 표시"""
    search_query = st.text_input(
        label="검색",
        placeholder="키워드를 검색하여 SNS 트렌드 레시피를 확인해보세요",
        key="search_input"
    )
    
    if search_query:
        results = [result for result in results if search_query.lower() in result["title"].lower()]
    
    total_pages = max(1, (len(results) - 1) // 3 + 1)
    page = st.slider("페이지", min_value=1, max_value=total_pages, value=st.session_state.index + 1)
    st.session_state.index = page - 1

    start_index = st.session_state.index * 3
    end_index = min(start_index + 3, len(results))

    for i, result in enumerate(results[start_index:end_index], start=start_index):
        with st.container():
            st.subheader(result["title"])
            col1, col2 = st.columns([2, 3])
            
            with col1:
                try:
                    video_link = result["link"]
                    if "/shorts/" in video_link:
                        video_id = video_link.split("/shorts/")[-1].split("?")[0]
                        video_link = f"https://www.youtube.com/embed/{video_id}"
                    st.video(video_link)
                except Exception as e:
                    st.error("동영상을 표시할 수 없습니다.")

            with col2:
                st.markdown(f'{result["view"]}, {result["upload_date"]}')
                if col2.button("✅선택", key=f"select_{i}"):
                    st.session_state.selected_recipe = result
                    st.session_state.modified_recipe = None
                    st.session_state.current_image = None
                    try:
                        video_id = result['link'].split('/')[-1].split("?")[0]
                        script = extract_text(video_id)
                        if script and script != "스크립트를 찾을 수 없습니다.":
                            content = {
                                "title": result["title"],
                                "script": script
                            }
                            st.session_state.selected_output = diet_recipe(content)
                        else:
                            st.warning("이 동영상의 자막을 찾을 수 없습니다.")
                    except Exception as e:
                        st.error(f"레시피 처리 오류: {str(e)}")
                        st.session_state.selected_output = None

            st.markdown("---")

    # 선택된 레시피 표시
    if st.session_state.selected_recipe and st.session_state.selected_output:
        try:
            clean_selected_output = clean_json_string(st.session_state.selected_output)
            output_json = json.loads(clean_selected_output)
            if output_json:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("### 🍱요리명")
                    st.write(output_json.get('title', '제목 없음'))
                    st.write("### 🥬재료")
                    st.write('✅' + output_json.get('ingredients', '재료 정보 없음'))
                    st.write("### 👨🏻‍🍳조리법")
                    st.write('✅' + output_json.get('steps', '조리법 정보 없음'))
                
                with col2:
                    st.write("#### 🎨 요리 이미지")
                    if not st.session_state.current_image:
                        with st.spinner("이미지 생성 중..."):
                            image_bytes = generate_recipe_image(
                                output_json.get('title', ''),
                                output_json.get('ingredients', '')
                            )
                            if image_bytes:
                                st.session_state.current_image = image_bytes
                                display_generated_image(image_bytes)
                            else:
                                st.warning("이미지를 생성할 수 없습니다.")
                    else:
                        display_generated_image(st.session_state.current_image)
                
                # 재료 변경 섹션
                st.write("### 🔄재료 변경")
                new_ingredient = st.chat_input("변경하고 싶은 재료를 입력하세요!")
                
                if new_ingredient:
                    with st.spinner("레시피 수정 중..."):
                        # 레시피 수정
                        st.session_state.modified_recipe = modify_recipe(
                            st.session_state.selected_output,
                            new_ingredient
                        )
                        
                        if st.session_state.modified_recipe:
                            modified_json = json.loads(clean_json_string(st.session_state.modified_recipe))
                            
                            # 수정된 레시피 표시
                            st.write("### ✨수정된 레시피")
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(modified_json.get('title', ''))
                                st.write("#### 재료")
                                st.write(modified_json.get('ingredients', ''))
                                st.write("#### 조리 과정")
                                st.write(modified_json.get('steps', ''))
                            
                            with col2:
                                st.write("#### 🎨 수정된 요리 이미지")
                                with st.spinner("수정된 레시피 이미지 생성 중..."):
                                    modified_image_bytes = generate_recipe_image(
                                        modified_json.get('title', ''),
                                        modified_json.get('ingredients', '')
                                    )
                                    if modified_image_bytes:
                                        display_generated_image(modified_image_bytes)
                                    else:
                                        st.warning("수정된 레시피의 이미지를 생성할 수 없습니다.")
                            
                            # 영양 정보 표시
                            st.write("### 🌿영양 정보")
                            with st.spinner("영양 정보 생성 중..."):
                                effect = effect_create(modified_json['title'].replace('##', '').strip())
                                if effect:
                                    st.write(effect)
                                else:
                                    st.warning("영양 정보를 생성할 수 없습니다.")
                
        except json.JSONDecodeError as e:
            st.error(f"JSON 파싱 오류: {str(e)}")
        except Exception as e:
            st.error(f"레시피 처리 중 오류가 발생했습니다: {str(e)}")
def main():
    # Set page configuration
    st.set_page_config(page_title="요리랩 레시피 변환 도우미", layout="wide")
    
    # Load and display the logo at the top of the sidebar
    logo_path = Path(__file__).parent / "img/logo.png"
    try:
        logo = Image.open(logo_path)
        st.sidebar.image(logo, use_column_width=True)
    except Exception as e:
        st.error(f"로고 이미지를 불러올 수 없습니다: {str(e)}")
    
    # Title and other sidebar or main content go here
    st.title("SNS Trend")
    
    try:
        results = load_data()
        display_recipes(results)
    except Exception as e:
        st.error(f"애플리케이션 오류: {str(e)}")

if __name__ == "__main__":
    main()