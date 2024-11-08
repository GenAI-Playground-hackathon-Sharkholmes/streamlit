from langchain_community.chat_models import BedrockChat
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# BedrockChat을 호출하는 함수 정의
def bedrock_chatbot():
    bedrock_llm = BedrockChat(
        credentials_profile_name='default', 
        model_id='anthropic.claude-3-sonnet-20240229-v1:0', 
        model_kwargs={
            "temperature": 0.5,  # 모델의 온도 값 설정
            "top_p": 1,          # 확률 누적 합계
            "top_k": 250         # 상위 k 토큰까지 선택
        }
    )
    return bedrock_llm

# 메모리 버퍼 설정 함수 정의
def buff_memory():
    buff_memory = bedrock_chatbot()
    memory = ConversationBufferMemory(llm=buff_memory, max_token_limit=200) 
    return memory

# 대화 체인 설정 함수 정의
def cvs_chain(input_text, memory):
    chain_data = bedrock_chatbot()
    cnvs_chain = ConversationChain(llm=chain_data, memory=memory, verbose=True)
    
    chat_reply = cnvs_chain.predict(input=input_text
                                    )
    return chat_reply





