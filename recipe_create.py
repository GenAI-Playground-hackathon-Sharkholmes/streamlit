import boto3
import json
import base64
from io import BytesIO
from PIL import Image
from youtube_transcript_api import YouTubeTranscriptApi
from botocore.config import Config
from botocore.exceptions import ClientError

# AWS 인증 정보 (실제 배포 시에는 환경변수나 secrets로 관리하세요)
AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"

def get_bedrock_client():
    """Bedrock 클라이언트 생성"""
    return boto3.client(
        "bedrock-runtime",
        region_name="us-east-1",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

def script_json(video_id):
    """유튜브 스크립트 추출"""
    try:
        # 유튜브 ID 정리 - 불필요한 파라미터 제거
        video_id = video_id.split('?')[0].split('&')[0]
        
        # 여러 언어 시도
        languages = ['ko', 'en', 'en-US', 'auto']
        transcript = None
        
        for lang in languages:
            try:
                if lang == 'auto':
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                else:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                if transcript:
                    break
            except Exception:
                continue
                
        if transcript:
            script = " ".join([item['text'] for item in transcript])
            return script
        else:
            return "스크립트를 찾을 수 없습니다."
            
    except Exception as e:
        print(f"동영상의 자막을 가져오지 못했습니다: {e}")
        return "스크립트를 찾을 수 없습니다."

def extract_text(video_id):
    """비디오 ID로부터 텍스트 추출"""
    return script_json(video_id)

def invoke_bedrock_model(client, prompt, max_tokens=512):
    """Bedrock 모델 호출 함수"""
    try:
        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        }
        response = client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(native_request)
        )
        return json.loads(response["body"].read())["content"][0]["text"]
    except Exception as e:
        print(f"Bedrock API 호출 실패: {str(e)}")
        return None

def diet_recipe(content):
    """레시피 생성 함수"""
    client = get_bedrock_client()
    query = f"""
            <Introduction>
            내가 음식이나 간식을 다루고 있는 영상 자막을 가지고 레시피를 추출하고자 해.
            </Introduction>
            <Input>
            {content}
            </Input>
            <OutputRequirements>
            If the input provides a diet recipe, summarize the 'title', 'ingredients', and 'steps'.
            However, if the input is not a recipe, create a diet recipe using the given ingredients.
            0. Try to know that which food this content introduces.
            1. Extract the food recipe title as concisely as possible, focusing on nouns.
            2. There may be a typo in the content, so please correct it and reflect it.
            3. Reflect the units of the ingredients.
            4. Specify the cooking time in the steps and write steps that match the ingredients.
            5. If you can't make recipes based on Input, return each as unknown.
            6. When you write down answer, only write content about food.
            7. 다른 말 추가하지 말고, outputexample대로만 출력해줘.
            . Answer in Korean.
            </OutputRequirements>
            <Outputexample>
            {{
                "title": "## 컬리플라워김치볶음밥",    
                "ingredients": "재료 (1인분)\\n 냉동 콜리플라워 1컵, 김치 1접시, 베이컨 3장, 달걀 1개, 올리브유 1스푼, 소금, 후추 약간",
                "steps": "만드는 법 (조리시간 10분)\\n1. 김치와 베이컨은 잘게 다져 주세요.\\n2. 달궈진 팬에 올리브유를 두르고, 냉동 컬리플라워를 수분이 날라가는 느낌으로 약불에서 볶아주세요. \\n3. 베이컨, 김치를 넣고 볶다가 약간의 소금과 후추를 넣고 마무리 해주세요.\\n4. 그릇에 담고, 달걀후라이를 얹어서 맛있게 드세요."
            }}
            </Outputexample>
            """
    return invoke_bedrock_model(client, query)

def modify_recipe(original_recipe, new_ingredient):
    """레시피 수정 함수"""
    client = get_bedrock_client()
    query = f"""
    다음 레시피를 '{new_ingredient}'를 사용하여 수정해주세요. 기존 레시피의 형식을 유지하면서 재료와 조리법을 적절히 변경해주세요.
    
    기존 레시피:
    {original_recipe}
    """
    return invoke_bedrock_model(client, query)

def generate_recipe_image(recipe_title, recipe_ingredients):
    """
    Bedrock의 Stable Diffusion을 사용하여 레시피 이미지 생성
    """
    client = get_bedrock_client()
    
    try:
        # 프롬프트 생성
        title = recipe_title.replace('##', '').strip()
        ingredients = recipe_ingredients.replace('재료 (1인분)', '').strip()
        
        # 한국어 프롬프트를 영어로 변환
        translation_prompt = f"""
        Translate the following Korean recipe title and ingredients to English for image generation.
        Keep only the main ingredients and key descriptive words. 
        Format the output as a simple description without any additional text:
        
        Title: {title}
        Ingredients: {ingredients}
        """
        
        english_desc = invoke_bedrock_model(client, translation_prompt)
        if not english_desc:
            return None
            
        # 불필요한 텍스트 제거
        english_desc = english_desc.strip().replace('"', '').replace('\n', ' ')
        
        # Stable Diffusion 프롬프트 구성
        body = {
            "text_prompts": [
                {
                    "text": f"professional food photography of {english_desc}, top view on a white plate, restaurant presentation, soft natural lighting, sharp focus, appetizing, garnished food photography",
                    "weight": 1.0
                },
                {
                    "text": "blurry, low quality, distorted, text, watermark, bad composition, amateur, cartoon, illustration",
                    "weight": -1.0
                }
            ],
            "cfg_scale": 7.0,
            "steps": 30,
            "seed": 42,
            "width": 512,
            "height": 512
        }
        
        # Stable Diffusion 모델 호출
        response = client.invoke_model(
            modelId="stability.stable-diffusion-xl-v1",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )
        
        if response and "body" in response:
            response_body = json.loads(response["body"].read())
            if "artifacts" in response_body and len(response_body["artifacts"]) > 0:
                image_data = response_body["artifacts"][0]["base64"]
                image_bytes = base64.b64decode(image_data)
                
                # 이미지 후처리
                image = Image.open(BytesIO(image_bytes))
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                return buffered.getvalue()
                
        return None
        
    except Exception as e:
        print(f"이미지 생성 실패: {str(e)}")
        return None

def effect_create(ingredients):
    """재료 효능 설명 생성"""
    client = get_bedrock_client()
    query = f"건강 레시피 및 다이어트 레시피를 소개하는 글을 작성하려고 해. 여기에 들어가는 대표 음식은 '{ingredients}'야.\n다른 대답은 제외하고, '{ingredients}'의 대표 효능만 5문장 내외의 줄글로 알려줄래?"
    return invoke_bedrock_model(client, query)