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
                 password="패스워드 입력",
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
        """CSV 파일에서 데이터를 로드하고 Couchbase에 저장"""
        print(f"데이터 로드 시작: {file_path}")
        data = pd.read_csv(file_path)
        total_rows = len(data)
        
        for idx, row in data.iterrows():
            try:
                doc_id = f"recipe_{uuid.uuid4()}"
                
                # 레시피 이름과 재료를 결합하여 벡터 생성
                combined_text = f"{row.get('name', '')} {row.get('ingredients', '')}"
                recipe_vector = self.generate_embedding(combined_text)
                
                doc_data = {
                    "id": row.get("id", ""),
                    "url": row.get("url", ""),
                    "name": row.get("name", ""),
                    "img": row.get("img", ""),
                    "summary": row.get("summary", ""),
                    "info1": row.get("info1", ""),
                    "info2": row.get("info2", ""),
                    "info3": row.get("info3", ""),
                    "ingredients": row.get("ingredients", ""),
                    "combined": row.get("combined", ""),
                    "recipe_vector": recipe_vector,
                    "type": "recipe"
                }
                
                self.collection.upsert(doc_id, doc_data)
                
                if idx % 100 == 0:
                    progress = (idx / total_rows) * 100
                    print(f"진행률: {progress:.2f}% ({idx}/{total_rows})")
                
            except Exception as e:
                print(f"문서 저장 중 오류 발생: {e}")
                continue
        
        print("데이터 로드 완료")

    def hybrid_search(self, query_text, limit=10):
        """하이브리드 검색 수행"""
        query_vector = self.generate_embedding(query_text)
        
        search_query = {
            "query": {
                "conjunction": {
                    "queries": [
                        {
                            "disjunction": {
                                "queries": [
                                    {
                                        "match": {
                                            "name": query_text,
                                            "boost": 1.5
                                        }
                                    },
                                    {
                                        "match": {
                                            "ingredients": query_text
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "vector": {
                                "field": "recipe_vector",
                                "vector": query_vector,
                                "boost": 1.0
                            }
                        }
                    ]
                }
            }
        }
        
        try:
            results = self.cluster.search_query(
                "recipe_vector_index",
                json.dumps(search_query),
                SearchOptions(limit=limit)
            )
            return results
        except Exception as e:
            print(f"검색 중 오류 발생: {e}")
            return []

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
            password="패스워드 입력"  # 실제 비밀번호로 변경하세요
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