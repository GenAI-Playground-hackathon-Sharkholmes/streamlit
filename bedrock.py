import streamlit as st
import json
import boto3
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from datetime import timedelta
import os

# 액세스 키를 환경 변수에 설정
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA2UC3BM3L4TJNAHCP'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'

# boto3 클라이언트 생성
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Couchbase 설정
COUCHBASE_HOST = "couchbase://3.35.104.117"
COUCHBASE_USERNAME = "Administrator" 
COUCHBASE_PASSWORD = "shark1234"
BUCKET_NAME = "recipes"

# Couchbase 연결 함수
def connect_couchbase():
    try:
        cluster = Cluster(COUCHBASE_HOST, ClusterOptions(PasswordAuthenticator(COUCHBASE_USERNAME, COUCHBASE_PASSWORD)))
        bucket = cluster.bucket(BUCKET_NAME)
        cluster.wait_until_ready(timedelta(seconds=5))
        return cluster, bucket.default_collection()
    except CouchbaseException as e:
        st.error(f"Error connecting to Couchbase: {e}")
        return None, None

# 재료 기반으로 Couchbase에서 레시피 검색
def get_recipe_by_ingredient(cluster, ingredient):
    search_result = cluster.search_query(
            "recipes._default.recipe-index",  # 인덱스 이름
            search_query,
            limit=10
        )
    #rows = cluster.query(query)
    #results = [row for row in rows]
    return search_result

# Claude 모델 API 호출 함수
def invoke_bedrock_model(original_recipe, modification_request):
    body_content = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "temperature": 1,
        "messages": [
            {
                "role": "user", 
                "content": f"Given this recipe: {original_recipe}. Please modify it as follows: {modification_request}"
            }
        ]
    }
    
    response = bedrock_client.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps(body_content).encode('utf-8'),
        contentType="application/json",
        accept="application/json"
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']

# Streamlit UI 
st.title("Bedrock 챗봇")
st.write("재료를 입력하고 레시피를 찾은 후, 기존 레시피에서 변경하고 싶은 사항을 입력하세요.")

# 재료 입력
ingredient = st.text_input("Enter ingredient:", "샐러드")
modification_request = st.text_input("Enter modification request (e.g., '닭가슴살 샐러드를 바질 샐러드로 바꿔줘')")

if st.button("Search Recipe"):
    cluster, collection = connect_couchbase()
    if collection:
        recipes = get_recipe_by_ingredient(cluster, ingredient)
        if recipes:
            st.write("### 검색된 레시피")
            recipe_data = recipes[0]  # 첫 번째 레시피 데이터 추출
            recipe_details = recipe_data.get('recipe', {})
            
            # 레시피 요약 텍스트 구성
            original_recipe = f"{recipe_details.get('name', 'No Name')} - {recipe_details.get('summary', 'No Summary')}"
            st.json(recipe_details)
            
            # 사용자 요청을 기반으로 Bedrock 모델 호출
            with st.spinner("Connecting to Bedrock..."):
                try:
                    modified_recipe = invoke_bedrock_model(original_recipe, modification_request)
                    st.write("### Modified Recipe")
                    st.write(modified_recipe)
                except Exception as e:
                    st.error(f"Error invoking Bedrock model: {e}")
        else:
            st.warning(f"No recipes found for ingredient: {ingredient}")
    else:
        st.error("Failed to connect to Couchbase.")