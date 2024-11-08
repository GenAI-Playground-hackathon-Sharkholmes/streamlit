import boto3
import json
from youtube_transcript_api import YouTubeTranscriptApi
from botocore.config import Config
from botocore.exceptions import ClientError
# AWS 인증 정보 설정
AWS_ACCESS_KEY_ID = "AKIA2UC3BM3L4TJNAHCP"
AWS_SECRET_ACCESS_KEY = "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"

def script_json(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en', 'en-US'])
        script = " ".join([item['text'] for item in transcript])
    except Exception as e:
        print(f"동영상의 자막을 가져오지 못했습니다: {e}")
        script = ""
    return script

def extract_text(video_id):
    return script_json(video_id)


def diet_recipe(content):
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
            3. Reflect the units of the ingredients, and substitute with exact diet-friendly ingredients if possible.
            4. Specify the cooking time in the steps and write steps that match the ingredients.
            5. If you can't make recipes based on Input, return each as unknown.
            6. When you write down answer, only write content about food.
            7. 다른 말 추가하지 말고, outputexample대로만 출력해줘.
            . Answer in Korean.
            </OutputRequirements>
            <Outputexample1>
            {{
                "title": "## 컬리플라워김치볶음밥",    
                "ingredients": "재료 (1인분)\\n 냉동 콜리플라워 1컵, 김치 1접시, 베이컨 3장, 달걀 1개, 올리브유 1스푼, 소금, 후추 약간",
                "steps": "만드는 법 (조리시간 10분)\\n1. 김치와 베이컨은 잘게 다져 주세요.\\n2. 달궈진 팬에 올리브유를 두르고, 냉동 컬리플라워를 수분이 날라가는 느낌으로 약불에서 볶아주세요. \\n3. 베이컨, 김치를 넣고 볶다가 약간의 소금과 후추를 넣고 마무리 해주세요.\\n4. 그릇에 담고, 달걀후라이를 얹어서 맛있게 드세요."
            }}
            </Outputexample1>
            <Outputexample2>
            {{
                "title": "## 곤약 낙지 볶음",    
                "ingredients": "재료 (1인분)\\n 낙지 1마리, 실곤약 1봉, 양파 1/4개, 청양고추 1/2개, 대파, 소금 약간, 양념장 (고추장 1T, 고춧가루 2T, 맛술 1T, 간장 1/2T, 다진 마늘 1T, 알룰로스 1T, 참기름 1T )",
                "steps": "만드는 법 (조리시간 20분)\\n1. 실곤약은 뜨거운 물에 살짝 데치고, 물기를 빼주세요. \\n2. 낙지는 깨끗이 씻은 후 적당한 크기로 잘라둡니다.\\n3. 양파와 대파는 먹기 좋은 크기로 자르고, 고추장, 고춧가루, 간장, 알룰로스, 참기름을 섞어 양념장을 만들어 주세요. \\n4. 팬에 참기름을 데우고 다진 마늘을 먼저 볶습니다.\\n5. 마늘향이 올라오면 양파, 낙지, 청양고추, 양념장을 넣고 잘 볶아 주세요.\\n6. 그릇에 물기를 뺀 실곤약을 담아 주고, 그 옆에 잘 볶아진 낙지를 담아 주세요. \\n7. 위에 깨소금을 솔솔 뿌려 마무리합니다."
            }}
            </Outputexample2>
            """

    print("=== Bedrock API 호출 시작 ===")
    print(f"입력 텍스트 길이: {len(content)} characters")

    try:
        # Create Bedrock client
        print("1. Bedrock 클라이언트 생성 시도...")
        client = boto3.client(
            "bedrock-runtime", 
            region_name="us-east-1",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        print("✓ 클라이언트 생성 성공")

        # Prepare request
        print("\n2. 요청 데이터 준비...")
        # 수정된 모델 ID
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"  # 올바른 모델 ID로 변경
        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0.5,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": query}],
                }
            ],
        }
        request = json.dumps(native_request)
        print("✓ 요청 데이터 준비 완료")
        print(f"\n요청 데이터 미리보기:")
        print(json.dumps(native_request, indent=2, ensure_ascii=False)[:500] + "...")

        # Invoke model
        print("\n3. 모델 호출 시도...")
        response = client.invoke_model(modelId=model_id, body=request)
        print("✓ 모델 호출 성공")
        print(f"응답 상태 코드: {response['ResponseMetadata']['HTTPStatusCode']}")

        # Process response
        print("\n4. 응답 처리...")
        model_response = json.loads(response["body"].read())
        response_text = model_response["content"][0]["text"]
        print("✓ 응답 처리 완료")
        print("\n응답 텍스트 미리보기:")
        print(response_text[:500] + "..." if len(response_text) > 500 else response_text)

        print("\n=== Bedrock API 호출 완료 ===")
        return response_text

    except ClientError as e:
        print("\n❌ AWS 서비스 에러 발생:")
        print(f"Error Code: {e.response['Error']['Code']}")
        print(f"Error Message: {e.response['Error']['Message']}")
        print(f"Request ID: {e.response['ResponseMetadata']['RequestId']}")
        return f"Error: AWS service error - {str(e)}"

    except Exception as e:
        print("\n❌ 예상치 못한 에러 발생:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        return f"Error: Unexpected error - {str(e)}"

def effect_create(ingredients):
    query = f"건강 레시피 및 다이어트 레시피를 소개하는 글을 작성하려고 해. 여기에 들어가는 대표 음식은 '{ingredients}'야.\n다른 대답은 제외하고, '{ingredients}'의 대표 효능만 5문장 내외의 줄글로 알려줄래?"
    
    return invoke_bedrock_claude(query)