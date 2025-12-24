# Class03 – Embedding 기반 이슈 분류 및 관측 로그

Class03에서는 기존 키워드 기반 분기에서 한 단계 더 나아가  
**임베딩을 활용한 이슈 분류(Routing)** 와  
그 결과를 관측 가능한 로그로 남기는 구조를 실험했다.

핵심 목표는 “LLM이 알아서 판단”이 아니라  
**의미 기반 분류를 코드로 통제**하는 것이었다.

---

## 무엇을 해봤나

### 1. Embedding 기반 이슈 분류(Router)

사용자 입력을 임베딩 벡터로 변환한 뒤,  
사전에 정의한 이슈 프로토타입(vpn, messenger, notification 등)과의
유사도를 비교해 **issue_type**을 결정했다.

```text
User Input
   ↓
Embedding
   ↓
Prototype Similarity 비교
   ↓
issue_type 결정 (vpn / notification / unknown)


- 키워드 변화에 비교적 강함
- 표현이 달라도 같은 이슈로 묶을 수 있음

---

### 2. Threshold 기반 Unknown 처리
임베딩 유사도가 기준값(threshold)보다 낮을 경우
억지로 분류하지 않고 **unknown**으로 처리했다.

이로 인해:
- 잡담성 문장
- 의미 없는 입력
- 일반 영어 문장

등이 KB 검색으로 흘러가는 것을 방지할 수 있었다.

---

### 3. 관측 로그(Observability)
Router 단계에서 다음 정보를 로그로 출력했다.

[Router] issue_type=vpn score=0.95

이를 통해:

왜 이런 분류가 나왔는지 추적 가능

threshold 조정 기준 확보

모델이 틀렸다 가 아닌 점수가 낮았다 로 설명 가능

4. 분류와 검색의 분리

Class03에서는 역할을 명확히 분리했다.

Router: 이슈 타입 분류만 담당

KB Search: 분류 결과를 기반으로 실행

이 구조 덕분에 이후 LangGraph, RAG 구조로 확장하기 쉬워졌다.

이 단계에서 느낀 점

Embedding은 정답을 바로 주기보다는
분류 품질을 안정화하는 도구에 가깝다는 느낌을 받았다.

Threshold와 관측 로그 없이는
임베딩 결과를 신뢰하기 어렵다는 것도 체감했다.

이후 LangGraph나 RAG로 넘어가기 위한 중간 단계로 적절했다.
```
