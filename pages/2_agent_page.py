import streamlit as st
import os
from PIL import Image
from slack_bot import SlackRecipeBot  # slack_recipe_bot.py 임포트

# Slack 설정
SLACK_BOT_TOKEN = "xoxb-4997656156160-7997102205702-DyekH4lzxr4rvWGNChSXVyFA"
CHANNEL_ID = "C07V95D03PY"

def create_recipe_card(recipe_data):
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        image_path = recipe_data["image"]
        if os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                st.image(image, use_column_width=True)
            except Exception as e:
                st.error(f"이미지를 불러오는데 실패했습니다: {e}")
        else:
            st.error(f"이미지 파일을 찾을 수 없습니다: {image_path}")
    
    with col2:
        st.markdown(f"<div class='recipe-title'>{recipe_data['title']}</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>재료</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='recipe-content'>{recipe_data['ingredients']}</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>👨‍🍳 조리법</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='recipe-content'>{recipe_data['steps']}</div>", unsafe_allow_html=True)
        
        # 출시하기 버튼 추가
        if st.button("✨ 출시하기", key=f"publish_{recipe_data['title']}", type="primary"):
            try:
                # 슬랙 메시지용 데이터 준비
                slack_recipe_data = {
                    "title": recipe_data['title'],
                    "ingredients": [item.strip() for item in recipe_data['ingredients'].split('•') if item.strip()],
                    "steps": [step.strip() for step in recipe_data['steps'].split('\n')[1:] if step.strip() and step.strip()[0].isdigit()],
                    "cooking_time": int(recipe_data['steps'].split('조리시간 ')[1].split('분')[0]),
                    "popular_with": [recipe_data['target_audience']],
                    "recipe_url": "https://recipe-url.com"  # 실제 URL로 교체 필요
                }
                
                # 슬랙봇으로 전송
                bot = SlackRecipeBot(SLACK_BOT_TOKEN)
                bot.send_recipe(CHANNEL_ID, slack_recipe_data)
                st.success(f"'{recipe_data['title']}' 레시피가 성공적으로 출시되었습니다! 🎉")
            except Exception as e:
                st.error(f"레시피 출시 중 오류가 발생했습니다: {str(e)}")
    
    with col3:
        st.markdown("### 평가지표")
        metrics_container = st.container()
        with metrics_container:
            st.metric("평균 머무르는 시간", f"{recipe_data['avg_time']}초")
            st.metric("클릭 비율", f"{recipe_data['click_rate']}%")
            st.markdown("**주요 타겟층**")
            st.markdown(recipe_data["target_audience"])
            st.metric("좋아요 수", recipe_data["likes"])

def main():
    st.set_page_config(layout="wide", page_title="레시피 대시보드")
    
    # Custom CSS
    st.markdown("""
        <style>
        .main > div {
            padding: 2rem;
        }
        
        .recipe-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .metric-container {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }

        .recipe-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }

        .section-title {
            font-size: 20px;
            font-weight: bold;
            margin: 15px 0;
        }

        .recipe-content {
            font-size: 18px;
            line-height: 1.8;
            margin-bottom: 20px;
        }
        
        /* 출시하기 버튼 스타일 */
        .stButton > button[data-baseweb="button"][kind="primary"] {
            background-color: #FF4B4B;
            color: white;
            margin-top: 20px;
            font-size: 16px;
        }
        
        .stButton > button[data-baseweb="button"][kind="primary"]:hover {
            background-color: #FF3333;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("레시피 분석 대시보드")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 샘플 레시피 데이터는 그대로 유지
    recipes = [
        {
            "title": "오크베리 아사이볼",
            "image": os.path.join(current_dir, "acai_bowl_image.jpg.png"),  # 로컬 파일 경로
            "ingredients": """• 냉동 오크베리 1컵
            • 바나나 1개
            • 그릭 요거트 1컵
            • 우유 1/2컵
            • 땅콩버터 2큰술
            • 그래놀라 1/2컵
            • 치아씨드 약간""",
            "steps": """만드는 법 (조리시간 10분)
            1. 냉동베리, 바나나, 그릭 요거트, 우유를 핸드블렌더나 믹서기에 갈아주세요.
            2. 컵에 갈아준 재료를 반정도 부어주세요.
            3. 땅콩버터를 취향에 맞게 넣어주세요.
            4. 그 위에 남은 갈아준 재료를 다시 부어주세요.
            5. 바나나, 그래놀라, 냉동베리, 치아씨드를 토핑으로 올려주면 완성입니다.""",
            "avg_time": 120,
            "click_rate": 45,
            "target_audience": "20대 여성",
            "likes": 234
        },
        {
            "title": "과일 요거트 아이스크림",
            "image": os.path.join(current_dir, "yogurt_icecream.png"),  # 로컬 파일 경로
            "ingredients": """재료 (1인분)
            • 요거트 아이스크림 1컵
            • 파인애플 1/2컵
            • 초코 시럽 1T
            • 몰티저스 아이스크림 토핑 1T""",
            "steps": """만드는 법 (조리시간 5분)
            1. 요거트 아이스크림을 그릇에 담습니다.
            2. 파인애플을 먹기 좋은 크기로 자릅니다.
            3. 아이스크림 위에 파인애플을 올립니다.
            4. 초코 시럽을 뿌립니다.
            5. 마지막으로 몰티저스 아이스크림 토핑을 올려 완성합니다.""",
            "avg_time": 90,
            "click_rate": 38,
            "target_audience": "10대 여성",
            "likes": 156
        },
        {
            "title": "통감자구이",
            "image": os.path.join(current_dir, "baked_potato.png"),  # 로컬 파일 경로
            "ingredients": """재료
            • 감자 4개
            • 소금 약간
            • 후추 약간
            • 올리브유 또는 버터 약간""",
            "steps": """만드는 법 (조리시간 40분)
            1. 감자를 씻어 껍질째 길게 자릅니다.
            2. 자른 감자를 소금, 후추로 밑간을 합니다.
            3. 팬에 올리브유 또는 버터를 두르고 감자를 굽습니다.
            4. 15분 정도 굽다가 뒤집어가며 계속 구워줍니다.
            5. 감자가 노릇노릇해지면 완성입니다.""",
            "avg_time": 150,
            "click_rate": 52,
            "target_audience": "40대 남성",
            "likes": 189
        }
    ]
    
    for recipe in recipes:
        st.markdown("---")
        create_recipe_card(recipe)

if __name__ == "__main__":
    main()
