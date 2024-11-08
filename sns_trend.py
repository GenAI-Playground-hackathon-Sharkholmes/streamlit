import streamlit as st
import pandas as pd
import json
import requests
from PIL import Image
from io import BytesIO
import os
import re
from recipe_create import diet_recipe, effect_create, extract_text

def clean_json_string(json_string):
    return re.sub(r'[\x00-\x1F\x7F]', '', json_string)

# Data loading
def load_data():
    youtube_df = pd.read_csv('./data/Youtube_search_df.csv')
    
    results = []
    
    # YouTube data
    for _, row in youtube_df.iterrows():
        results.append({
            'type': 'youtube',
            'title': row['title'],
            'link': row['url'],
            'view': row['view'],
            'upload_date': row['upload_date']
        })
        
    return results

def display_recipes(results):
    st.header("SNS Trend🧑‍🍳")
    search_query = st.text_input("키워드 검색 시 관련 레시피만 보여져요🍳", "")
    
    if search_query:
        results = [result for result in results if search_query.lower() in result["title"].lower()]
    
    if 'index' not in st.session_state:
        st.session_state.index = 0
    if 'selected_recipe' not in st.session_state:
        st.session_state['selected_recipe'] = None

    total_pages = (len(results) - 1) // 3 + 1
    page = st.slider("", 1, total_pages, st.session_state.index + 1)
    st.session_state.index = page - 1

    start_index = st.session_state.index * 3
    end_index = start_index + 3
    end_index = min(end_index, len(results))

    for i, result in enumerate(results[start_index:end_index], start=start_index):
        with st.container():
            st.subheader(result["title"])
            col1, col2 = st.columns([2, 3])
            
            with col1:
                video_link = result["link"].replace("/shorts/", "/embed/") if "/shorts/" in result["link"] else result["link"]
                st.video(video_link)

            with col2:
                st.markdown(f'{result["view"]}, {result["upload_date"]}')
                if col2.button("✅선택", key=f"select_{i}"):
                    st.session_state.selected_recipe = result
                    video_id = result['link'].split('/')[-1].replace('-', '_').replace('.', '_')
                    script = extract_text(video_id)
                    content = {
                        "title": result["title"],
                        "script": script
                    }
                    st.session_state.selected_output = diet_recipe(content)

            st.markdown("---")

    if st.session_state.selected_recipe:
        selected_output = st.session_state.selected_output
        clean_selected_output = clean_json_string(selected_output)
        try:
            output_json = json.loads(clean_selected_output)
            if output_json:
                st.write("### 🍱요리명")
                st.write(output_json.get('title', 'Title not available'))
                st.write("### 🥬재료")
                st.write('✅' + output_json.get('ingredients', 'Ingredients not available'))
                st.write("### 👨🏻‍🍳조리법")
                st.write('✅' + output_json.get('steps', 'Steps not available'))
        except json.JSONDecodeError as e:
            st.error(f"JSON 파싱 오류: {e}")

def additional():
    ingredients = st.chat_input("재료를 입력하면 효능을 생성해드려요!")
    if ingredients:
        st.subheader(f'{ingredients}의 효능')
        st.write(effect_create(ingredients))
        st.image("https://via.placeholder.com/500", caption="Generated Image")

def main():
    results = load_data()
    display_recipes(results)
    additional()

if __name__ == "__main__":
    main()