from couchbase.options import ClusterOptions, ClusterTimeoutOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.management.search import SearchIndex
from couchbase.options import SearchOptions  # SearchOptions의 올바른 import 경로
from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
import uuid
import json
from datetime import timedelta
import requests
import socket

class RecipeSearchManager:
    def __init__(self, host="localhost",
                 username="Administrator", 
                 password="PASSWORD",
                 bucket_name="recipes"):
        try:
            # 모든 포트를 명시적으로 지정한 연결 문자열
            connection_string = (
                f"couchbase://{host}?"
                f"management_port=8091"
                f"&kv_port=11210"
                f"&view_port=8092"
                f"&query_port=8093"
                f"&search_port=8094"
                f"&analytics_port=8095"
                f"&eventing_port=8096"
            )
            
            # 인증 설정
            auth = PasswordAuthenticator(username, password)
            
            # 타임아웃 설정
            timeout_options = ClusterTimeoutOptions(
                connect_timeout=timedelta(seconds=30),
                key_value_timeout=timedelta(seconds=25),
                query_timeout=timedelta(seconds=25)
            )
            
            # 클러스터 옵션 설정
            options = ClusterOptions(auth)
            options.timeout_options = timeout_options
            
            print(f"Couchbase 연결 시도 중...")
            print(f"Host: {host}")
            print(f"연결 문자열: {connection_string}")
            
            # 클러스터 연결
            self.cluster = Cluster(connection_string, options)
            
            # 버킷 연결
            self.bucket_name = bucket_name
            self.bucket = self.cluster.bucket(bucket_name)
            self.collection = self.bucket.default_collection()
            
            print(f"Couchbase에 성공적으로 연결되었습니다.")
            print(f"- 버킷: {bucket_name}")
            
            # 한국어 지원 모델 로드
            self.model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')
            print("텍스트 임베딩 모델 로드 완료")
            
        except Exception as e:
            print(f"Couchbase 연결 중 오류 발생:")
            print(f"- 오류 유형: {type(e).__name__}")
            print(f"- 오류 메시지: {str(e)}")
            raise

    def create_vector_index(self):
        """벡터 검색을 위한 인덱스 생성"""
        index_definition = {
            "type": "fulltext-index",
            "name": "recipe_vector_index",
            "sourceName": self.bucket_name,
            "params": {
                "mapping": {
                    "types": {
                        "recipe": {
                            "enabled": True,
                            "properties": {
                                "name": {
                                    "enabled": True,
                                    "dynamic": False,
                                    "fields": [{
                                        "name": "name",
                                        "type": "text",
                                        "analyzer": "korean",
                                    }]
                                },
                                "ingredients": {
                                    "enabled": True,
                                    "dynamic": False,
                                    "fields": [{
                                        "name": "ingredients",
                                        "type": "text",
                                        "analyzer": "korean",
                                    }]
                                },
                                "recipe_vector": {
                                    "enabled": True,
                                    "dynamic": False,
                                    "fields": [{
                                        "name": "recipe_vector",
                                        "type": "vector",
                                        "dims": 768,
                                        "similarity": "cosine"
                                    }]
                                }
                            }
                        }
                    }
                },
                "analysis": {
                    "analyzers": {
                        "korean": {
                            "type": "custom",
                            "tokenizer": "unicode",
                            "token_filters": ["lowercase", "cjk_width", "cjk_bigram"]
                        }
                    }
                }
            }
        }
        
        try:
            self.cluster.search_indexes().create_index(SearchIndex.from_dict(index_definition))
            print("벡터 검색 인덱스가 생성되었습니다.")
        except Exception as e:
            print(f"인덱스 생성 중 오류 (이미 존재할 수 있음): {e}")

    def generate_embedding(self, text):
        """텍스트를 벡터로 변환"""
        return self.model.encode(text).tolist()

    def load_data(self, file_path):
        try:
            # CSV 파일 읽기
            data = pd.read_csv(file_path)
            print(f"총 레시피 수: {len(data)}")
            total_rows = len(data)
            
            for idx, row in data.iterrows():
                try:
                    doc_id = f"recipe_{uuid.uuid4()}"
                    
                    # 레시피 이름과 재료를 결합하여 벡터 생성 (오타 수정: RecipeNmae -> RecipeName)
                    name = str(row['RecipeName']) if not pd.isna(row['RecipeName']) else ''
                    ingredients = str(row['Ingredients_pre']) if not pd.isna(row['Ingredients_pre']) else ''
                    
                    combined_text = f"{name} {ingredients}".strip()
                    recipe_vector = self.generate_embedding(combined_text)
                    
                    # 데이터 구성 (original column names 사용)
                    doc_data = {
                        "id": str(idx),
                        "name": name,
                        "url": str(row['URL']) if not pd.isna(row['URL']) else '',
                        "img": str(row['Image']) if not pd.isna(row['Image']) else '',
                        "summary": str(row['Summary']) if not pd.isna(row['Summary']) else '',
                        "info1": str(row['Steps']) if not pd.isna(row['Steps']) else '',
                        "info2": str(row['ingredients']) if not pd.isna(row['ingredients']) else '',
                        "info3": '',
                        "ingredients": ingredients,
                        "combined": combined_text,
                        "recipe_vector": recipe_vector,
                        "type": "recipe"
                    }
                    
                    # 데이터 검증
                    if not name or not ingredients:
                        print(f"경고: {idx}번 레시피의 이름 또는 재료가 비어 있습니다.")
                        print(f"- 이름: {name}")
                        print(f"- 재료: {ingredients}")
                    
                    # 데이터 저장
                    self.collection.upsert(doc_id, doc_data)
                    
                    if idx % 100 == 0:
                        progress = (idx / total_rows) * 100
                        print(f"진행률: {progress:.2f}% ({idx}/{total_rows})")
                        print(f"샘플 데이터 (id: {doc_id}):")
                        print(f"- 이름: {doc_data['name']}")
                        print(f"- 재료: {doc_data['ingredients'][:100]}...")
                        print(f"- URL: {doc_data['url']}")
                        print("-" * 50)
                    
                except Exception as e:
                    print(f"문서 {idx}번 저장 중 오류 발생: {e}")
                    print("문제의 행:")
                    print(row)
                    continue
            
            print("데이터 로드 완료")
            print(f"총 처리된 레시피 수: {total_rows}")
            
        except Exception as e:
            print(f"CSV 파일 처리 중 오류 발생: {e}")
            raise

def verify_ports():
    """모든 필요한 포트의 연결 상태 확인"""
    ports = [8091, 8092, 8093, 8094, 8095, 8096, 11210, 11211]
    
    print("포트 연결 상태 확인 중...")
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        status = "열림" if result == 0 else "닫힘"
        print(f"포트 {port}: {status}")
        sock.close()

def main():
    try:
        # 1. 포트 연결 상태 확인
        print("Couchbase 포트 연결 상태 확인...")
        verify_ports()
        
        # 2. RecipeSearchManager 초기화
        print("\nRecipeSearchManager 초기화 중...")
        manager = RecipeSearchManager(
            username="Administrator",
            password="shark1234"  # 실제 비밀번호로 변경하세요
        )
        
        # 3. 검색 인덱스 생성
        print("\n검색 인덱스 생성 중...")
        manager.create_vector_index()
        
        # 4. 데이터 로드
        print("\n데이터 로드 중...")
        csv_file_path = "../data/dw_recipes_fin1.csv"
        manager.load_data(csv_file_path)
        
        # 5. 검색 테스트
        print("\n검색 테스트 수행 중...")
        test_queries = ["매운 찌개", "간단한 요리", "건강식"]
        
        for query in test_queries:
            print(f"\n'{query}' 검색 결과:")
            results = manager.hybrid_search(query)
            
            for hit in results:
                doc = manager.collection.get(hit.id).content
                print(f"레시피: {doc['name']}")
                print(f"재료: {doc['ingredients']}")
                print(f"유사도 점수: {hit.score}")
                print("-" * 50)
        
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()