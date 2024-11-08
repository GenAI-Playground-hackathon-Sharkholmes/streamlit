import streamlit as st
from PIL import Image
import io

def get_dummy_image(width=300, height=200, color='gray'):
    img = Image.new('RGB', (width, height), color=color)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def create_section(title, images, start_idx):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    
    # Initialize session state for this section if not exists
    if f'show_more_{start_idx}' not in st.session_state:
        st.session_state[f'show_more_{start_idx}'] = False
    
    # 기본적으로 3개만 보여주기
    display_count = len(images) if st.session_state[f'show_more_{start_idx}'] else 3
    
    # Create rows of 3 items each
    for row_idx in range(0, display_count, 3):
        cols = st.columns(3)
        for col_idx in range(3):
            item_idx = row_idx + col_idx
            if item_idx < display_count:
                with cols[col_idx]:
                    st.image(images[item_idx]["image"], use_column_width=True)
                    st.markdown(f'<div class="recipe-title">{images[item_idx]["recipe"]}</div>', unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="metadata">'
                        f'<span>{images[item_idx]["date"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    if st.button("자세히 보기", key=f"btn_{start_idx}_{item_idx}", use_container_width=True):
                        st.session_state.selected_item = f"{start_idx}_{item_idx}"
    
    # Show more/less button if there are more than 3 items
    if len(images) > 3:
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            if st.button(
                "접기" if st.session_state[f'show_more_{start_idx}'] else "더보기",
                key=f"more_{start_idx}",
                use_container_width=True
            ):
                st.session_state[f'show_more_{start_idx}'] = not st.session_state[f'show_more_{start_idx}']
                st.rerun()

def main():
    st.set_page_config(layout="wide", page_title="채팅 히스토리")
    
    # Custom CSS
    st.markdown("""
        <style>
        /* General layout */
        .main > div {
            padding: 0 !important;
        }
        
        /* Section styling */
        .section-title {
            font-size: 20px;
            font-weight: 600;
            color: #333;
            margin: 30px 0 20px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }
        
        /* Recipe card styling */
        div[data-testid="column"] {
            background: white;
            border-radius: 12px;
            padding: 10px;
            margin: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease;
        }
        
        div[data-testid="column"]:hover {
            transform: translateY(-5px);
        }
        
        .recipe-title {
            font-size: 15px;
            font-weight: 500;
            margin: 10px 0;
            color: #1a1a1a;
        }
        
        .metadata {
            color: #666;
            font-size: 13px;
            margin-bottom: 10px;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #f0f2f6;
            color: #333;
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            transition: background-color 0.2s ease;
        }
        
        .stButton > button:hover {
            background-color: #e6e9ef;
        }
        
        /* Image styling */
        img {
            border-radius: 8px;
            object-fit: cover;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([4,1])
    with col1:
        st.title("AGENT 관리 페이지")
    with col2:
        st.button("New Chat", type="secondary", use_container_width=True)
        
    # Sample data for each section (더 많은 아이템 추가)
    sections = {
        "새롭게 생성된 레시피별 대쉬보드 페르소나 별 평가지표": [
            {"image": get_dummy_image(color='#FFE4E1'), "recipe": "봄나물 비빔밥", "date": "2024.04.15"},
            {"image": get_dummy_image(color='#FFE4E1'), "recipe": "된장찌개", "date": "2024.04.15"},
            {"image": get_dummy_image(color='#FFE4E1'), "recipe": "나물무침", "date": "2024.04.15"},
            {"image": get_dummy_image(color='#FFE4E1'), "recipe": "김치찜", "date": "2024.04.15"},
            {"image": get_dummy_image(color='#FFE4E1'), "recipe": "갈비찜", "date": "2024.04.15"},
            {"image": get_dummy_image(color='#FFE4E1'), "recipe": "미역국", "date": "2024.04.15"}
        ],
        "요아정": [
            {"image": get_dummy_image(color='#E6E6FA'), "recipe": "김치찌개", "date": "2024.04.14"},
            {"image": get_dummy_image(color='#E6E6FA'), "recipe": "제육볶음", "date": "2024.04.14"},
            {"image": get_dummy_image(color='#E6E6FA'), "recipe": "간장계란밥", "date": "2024.04.14"},
            {"image": get_dummy_image(color='#E6E6FA'), "recipe": "찜닭", "date": "2024.04.14"},
            {"image": get_dummy_image(color='#E6E6FA'), "recipe": "부대찌개", "date": "2024.04.14"}
        ],
        "오뚜기 - 바로 간단하게 식사 준비 끝!": [
            {"image": get_dummy_image(color='#F0FFF0'), "recipe": "3분 카레", "date": "2024.04.13"},
            {"image": get_dummy_image(color='#F0FFF0'), "recipe": "즉석 냉면", "date": "2024.04.13"},
            {"image": get_dummy_image(color='#F0FFF0'), "recipe": "컵밥", "date": "2024.04.13"},
            {"image": get_dummy_image(color='#F0FFF0'), "recipe": "라면", "date": "2024.04.13"},
            {"image": get_dummy_image(color='#F0FFF0'), "recipe": "즉석죽", "date": "2024.04.13"},
            {"image": get_dummy_image(color='#F0FFF0'), "recipe": "컵스프", "date": "2024.04.13"}
        ]
    }
    
    # Create sections
    for idx, (title, images) in enumerate(sections.items()):
        create_section(title, images, idx)
        
        # Add separator except for last section
        if idx < len(sections) - 1:
            st.markdown("<hr style='margin: 30px 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()