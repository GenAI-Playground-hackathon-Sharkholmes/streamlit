# 📁 pages/sns_trends.py
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
    blog_df = pd.read_csv('./data/blog_.csv')
    with open('./data/output_0411.json', 'r', encoding='utf-8') as file:
        youtube_results = json.load(file)
    
    results = []
    
    # YouTube data
    for item in youtube_results:
        results.append({
            'type': 'youtube',
            'title': item['title'],
            'description': item['description'],
            'link': item['link'],
            'view': item.get('view', 'N/A'),
            'channel_title': item.get('channel_title', 'N/A')
        })

    # Blog data
    for _, row in blog_df.iterrows():
        results.append({
            'type': 'blog',
            'title': row['title'],
            'description': row['content'],
            'link': row['link'],
            'thumbnail': row['img']
        })
        
    return results

def display_recipes(results, tab_type):
    st.header("SNS Trend🧑‍🍳")
    search_query = st.text_input("키워드 검색 시 관련 레시피만 보여져요🍳", "", key=f'search_{tab_type}')
    
    if search_query:
        results = [result for result in results if search_query.lower() in result["title"].lower()]
    
    if tab_type != "Total":
        results = [result for result in results if result['type'] == tab_type.lower()]
    
    if 'index' not in st.session_state:
        st.session_state.index = 0
    if 'selected_recipe' not in st.session_state:
        st.session_state['selected_recipe'] = None

    total_pages = (len(results) - 1) // 3 + 1
    page = st.slider("", 1, total_pages, st.session_state.index + 1, key=f'page_{tab_type}')
    st.session_state.index = page - 1

    start_index = st.session_state.index * 3
    end_index = start_index + 3
    end_index = min(end_index, len(results))

    for i, result in enumerate(results[start_index:end_index], start=start_index):
        with st.container():
            st.subheader(result["title"])
            col1, col2 = st.columns([2, 3])
            
            with col1:
                if result["type"] == "youtube":
                    video_link = result["link"].replace("/shorts/", "/embed/") if "/shorts/" in result["link"] else result["link"]
                    st.video(video_link)
                elif result["type"] == "blog":
                    if result['thumbnail']:
                        try:
                            response = requests.get(result["thumbnail"])
                            image = Image.open(BytesIO(response.content))
                            st.image(image, caption='Uploaded Image', use_column_width=True)
                        except:
                            image_response = requests.get(result['thumbnail'])
                            if image_response.status_code == 200:
                                image_path = f"./tmp_img_{i}_{tab_type}.jpg"
                                with open(image_path, 'wb') as file:
                                    file.write(image_response.content)
                                st.markdown(f"""
                                <div style="position: relative; width: 300px;">
                                    <img src="{image_path}" style="width: 100%;" />
                                </div>
                                """, unsafe_allow_html=True)

            with col2:
                if result["type"] == "youtube":
                    st.write(result["description"][:150] + '...')
                    st.markdown(f'조회수 {result["view"]}, 채널명 {result["channel_title"]}')
                    if col2.button("✅선택", key=f"select_{tab_type}_{i}"):
                        st.session_state.selected_recipe = result
                        video_id = result['link'].split('/')[-1].replace('-', '_').replace('.', '_')
                        script = extract_text(video_id)
                        content = {
                            "title": result["title"],
                            "description": result["description"],
                            "script": script
                        }
                        st.session_state.selected_output = diet_recipe(content)
                elif result["type"] == "blog":
                    st.markdown(f"[{result['link']}]({result['link']})", unsafe_allow_html=True)
                    st.write(result["description"].split('\n')[0])
                    hashtags = [tag for tag in result["description"].split() if tag.startswith('#')]
                    st.markdown(" ".join(hashtags))
                    if col2.button("✅선택", key=f"select_{tab_type}_{i}"):
                        st.session_state.selected_recipe = result
                        content = {
                            "title": result["title"],
                            "content": result["description"]
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
    tab = st.tabs(["Total", "YouTube", "Blog"])
    with tab[0]:
        display_recipes(results, "Total")
    with tab[1]:
        display_recipes(results, "YouTube")
    with tab[2]:
        display_recipes(results, "Blog")
    additional()

    # Cleanup downloaded images
    for i in range(len(results)):
        for tab_type in ["Total", "YouTube", "Blog"]:
            image_path = f"./tmp_img_{i}_{tab_type}.jpg"
            if os.path.exists(image_path):
                os.remove(image_path)

if __name__ == "__main__":
    main()
