from openai import OpenAI
import json
from youtube_transcript_api import YouTubeTranscriptApi

def script_json(video_id):
    try:
        # 동영상의 자막을 가져옵니다.
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en', 'en-US'])
        script = " ".join([item['text'] for item in transcript])
        # 자막 데이터를 JSON 파일로 저장합니다.
        #with open(f'script_{video_id}.json', 'w', encoding='utf-8') as json_file:
         #   json.dump(transcript, json_file, ensure_ascii=False, indent=4)
        #print(f"자막 데이터가 'script_{video_id}.json' 파일로 저장되었습니다.")
    except Exception as e:
        print(f"동영상의 자막을 가져오지 못했습니다: {e}")
        script=""
    return script


def extract_text(video_id):
  # 자막 스크립트 가져오기
    script = script_json(video_id)
    # 전체 텍스트를 결합하여 반환
    return script
  
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="",
)

def diet_recipe(content):
    query = f"""
            <Introduction>
            I'm trying to convert existing recipes to develop healthy diet recipes.
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
            . Answer in Korean.
            </OutputRequirements>
            <Outputexample1>
            {{
                "title": "## 컬리플라워김치볶음밥",	
                "ingredients": "재료 (1인분)\n 냉동 콜리플라워 1컵, 김치 1접시, 베이컨 3장, 달걀 1개, 올리브유 1스푼, 소금, 후추 약간",
                "steps": "만드는 법 (조리시간 10분)\n1. 김치와 베이컨은 잘게 다져 주세요.\n2. 달궈진 팬에 올리브유를 두르고, 냉동 컬리플라워를 수분이 날라가는 느낌으로 약불에서 볶아주세요. \n3. 베이컨, 김치를 넣고 볶다가 약간의 소금과 후추를 넣고 마무리 해주세요.\n4. 그릇에 담고, 달걀후라이를 얹어서 맛있게 드세요."
            }}
            </Outputexample1>
            <Outputexample2>
             {{
                "title": "## 곤약 낙지 볶음",	
                "ingredients": "재료 (1인분)\n 
                낙지 1마리, 실곤약 1봉, 양파 1/4개, 청양고추 1/2개, 대파, 소금 약간, 양념장 (고추장 1T, 고춧가루 2T, 맛술 1T, 간장 1/2T, 다진 마늘 1T, 알룰로스 1T, 참기름 1T )
",
                "steps": "만드는 법 (조리시간 20분)\n
1. 실곤약은 뜨거운 물에 살짝 데치고, 물기를 빼주세요. \n
2. 낙지는 깨끗이 씻은 후 적당한 크기로 잘라둡니다.\n
3. 양파와 대파는 먹기 좋은 크기로 자르고, 고추장, 고춧가루, 간장, 알룰로스, 참기름을 섞어 양념장을 만들어 주세요. \n
4. 팬에 참기름을 데우고 다진 마늘을 먼저 볶습니다.\n
5. 마늘향이 올라오면 양파, 낙지, 청양고추, 양념장을 넣고 잘 볶아 주세요.\n
6. 그릇에 물기를 뺀 실곤약을 담아 주고, 그 옆에 잘 볶아진 낙지를 담아 주세요. \n
7. 위에 깨소금을 솔솔 뿌려 마무리합니다.
"
            }}
            </Outputexample2>
            """
    
    # 메시지 설정
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
        "role": "system",
        "content": "You are a very kind and smart nutritionist."
    }, {
        "role": "user",
        "content": query
    }])

    # ChatGPT API 호출하기
    output_text = response.choices[0].message.content.strip()
    return output_text
  
def effect_create(ingredients):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
              {"role": "system", "content": "You are a very kind and smart nutritionist."},
              {"role": "user", 
               "content": f"건강 레시피 및 다이어트 레시피를 소개하는 글을 작성하려고 해. 여기에 들어가는 대표 음식은 '{ingredients}'야.\ 다른 대답은 제외하고, '{ingredients}'의 대표 효능만 5문장 내외의 줄글로 알려줄래?"}
        ]
    )
    output_text = response.choices[0].message.content.strip()
    return output_text
