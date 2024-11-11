## 숙명여대 캠퍼스타운 X AWS GenAI Playground hackathon : YORILAB
<img width="1920" alt="Frame 1" src="https://github.com/user-attachments/assets/aaaa9b4f-1901-4e83-89b7-5b9057597266">

<br>

### YORILAB : 신메뉴 개발 시장 반응 예측 AI 서비스
- 데이터 수집과 AI 기술을 접목하여 기존 R&D 프로세스의 효율성을 극대화
- 식품 R&D 부서를 페르소나로 삼아 새로운 레시피 개발과 시장 반응 예측을 일원화하는 AI 솔루션을 구현
- Bedrock Agent 활용한 피드백  분석
- 대체 재료를 활용한 차별화된 레시피 구상

### ❗️ Introduction
YoriLab은 SNS 데이터와 AI를 활용해 실시간으로 음식 트렌드를 분석하고 소비자 반응을 예측하여 R&D 효율을 높이는 서비스입니다. Gen AI를 활용하여 신제품 개발 시장 반응을 예측하는 AI 서비스, YoriLab은 데이터 수집과 AI 기술을 접목하여 R&D 프로세스의 효율성을 극대화하는 데 중점을 두고 설계되었습니다. 특히, 식품 R&D 부서를 페르소나로 삼아 새로운 레시피 개발과 시장 반응 예측을 일원화하는 AI 솔루션을 구현한 점이 큰 특징입니다. 기존의 복잡한 신제품 개발 과정에서 YoriLab은 데이터와 AI를 활용하여 트렌드를 빠르게 분석하고, 소비자 반응을 예측함으로써 효율성을 높이고 자동화된 솔루션을 제공합니다. 
<br>
1. Amazon Bedrock 기반의 AI 페르소나
2. Couchbase 데이터베이스와 벡터 인덱스 활용
3. 데이터 파이프라인 구축과 트렌드 분석 자동화
<br>
<img width="764" alt="스크린샷 2024-11-11 오후 12 40 59" src="https://github.com/user-attachments/assets/842f3f2b-8499-404c-ae73-58521dc8e9ad">
<br>

<br>


### 🔧 Technology Used
| Couchbase | AWS Bedrock | AWS Sagemaker |
| --- | --- |--- |

<br>

### 🛠 Project Architecture
<img width="647" alt="스크린샷 2024-11-11 오후 12 36 32" src="https://github.com/user-attachments/assets/45a7d256-6951-4e68-ba2f-8ec874011dec">

<br>

### Feature Overview
#### 1️⃣ SNS 기반 레시피 생성 및 이미지 생성
데이터를 통해 SNS 트렌드를 분석하고 이를 바탕으로 최신 레시피와 이미지를 자동 생성합니다. 출시 전 시제품 대신 AI로 생성한 이미지를 활용해 소비자 반응을 예측할 수 있습니다.

#### 2️⃣ 레시피 검색 및 변형
특정 재료를 기반으로 기존 레시피를 변형하거나 새로운 레시피를 자동 생성할 수 있습니다. AI 이미지를 통해 다양한 옵션을 신속하게 시도해볼 수 있어 R&D 속도와 효율성이 크게 향상됩니다.

#### 3️⃣ 대시보드 기반 소비자 반응 예측 및 슬랙봇 연동
출시 전 다양한 소비자 페르소나(예: 20대 대학생, 30대 직장인 등)를 설정하여 제품의 반응을 평가합니다. Amazon Bedrock Agent의 AI 페르소나를 활용하여 출시 전 다양한 소비자 유형에 대한 반응을 테스트하고 예측합니다. 반응이 일정 기준을 넘으면 슬랙 알림을 통해 R&D 팀에 출시 진행을 알리는 기능도 구현했습니다.



<br>


### 기대효과
#### 1️⃣ 전통적인 R&D 방식 개선
SNS 데이터 실시간 수집을 통해 AI 기반 소비자 선호도 예측 시스템 구축

#### 2️⃣ 트렌드 분석에서 소비자 예측 및 제품화까지 과정 자동화
신제품 기획부터 출시까지 일원화된 시스템
연구개발 단계별 자동화 솔루션 도입

<br>

### 🎥 시연영상
<img width="809" alt="스크린샷 2024-11-11 오후 5 23 30" src="https://github.com/user-attachments/assets/67f87f57-4ce5-456d-89e8-8f8b47579743">
<img width="815" alt="스크린샷 2024-11-11 오후 5 23 58" src="https://github.com/user-attachments/assets/2692a906-29ef-4e1c-89c1-b3e0cb93e40c">
<img width="808" alt="스크린샷 2024-11-11 오후 5 24 16" src="https://github.com/user-attachments/assets/c2b6d915-8b91-408c-9fab-344496548d39">


<br>

### 팀원 및 역할
| 검색엔진 | 레시피 이미지 생성 | 레시피 챗봇 | 
|:----------:|:----------:|:----------:|
|[<img src="https://avatars.githubusercontent.com/u/139690326?v=4" alt="" style="width:100px;100px;">](https://github.com/leedoming) <br/><div align="center">이수민</div> |[<img src="https://avatars.githubusercontent.com/u/158597024?v=4" alt="" style="width:100px;100px;">](https://github.com/maeilej)  <br/><div align="center">이은지</div> | [<img src="https://avatars.githubusercontent.com/u/80513699?v=4" alt="" style="width:100px;100px;">](https://github.com/ahyeon-github) <br/><div align="center">임아현</div>




