import os
from langchain_aws import ChatBedrock
from langchain.schema import HumanMessage

# Bedrock chatbot 호출 함수 정의
def bedrock_chatbot(input_text):
    # ChatBedrock 객체 생성
    bedrock_llm = ChatBedrock(
        credentials_profile_name='default',  # AWS 자격증명 프로파일 설정
        model_id='anthropic.claude-3-sonnet-20240229-v1:0',  # 사용할 모델 ID 설정
        model_kwargs={
            "temperature": 0.5,  # 모델의 온도 값 설정
            "top_p": 1,          # 확률 누적 합계
            "top_k": 250         # 상위 k 토큰까지 선택
        }
    )
    
    # 메시지 포맷 맞춰서 생성
    messages = [HumanMessage(content=input_text)]
    
    # 모델 호출 및 응답 반환
    return bedrock_llm.invoke(messages)

# 테스트
response = bedrock_chatbot("오늘 저녁 메뉴 추천해줘")
print(response)