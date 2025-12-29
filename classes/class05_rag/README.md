# Class05 – Embedding 기반 RAG (Score 관측 단계)

Class05에서는 키워드 매칭을 완전히 제거하고  
**Embedding + Vector Search(FAISS)** 기반 RAG 구조를 구성했다.

이 단계의 목적은  
“정답을 고르는 것”이 아니라  
**RAG가 실제로 어떤 점수와 결과를 반환하는지 관측하는 것**이다.

---

## 이번 단계의 핵심 방향

- RAG 검색 결과를 **걸러내지 않는다**
- similarity score를 **판단 기준으로 사용하지 않는다**
- 대신, 모든 score를 **로그로 남긴다**

즉,  
**Precision을 높이기 전, Recall과 분포를 먼저 본다**는 전략이다.

---

## 전체 흐름

User Input
↓
Embedding 변환
↓
FAISS Vector Search (top-k)
↓
KB + similarity score 반환
↓
LLM 응답 생성

이 단계에서는:

- score가 낮아도 KB는 그대로 전달
- LLM이 KB를 참고해 안내 문장을 생성

---

## SearchKBTool 설계 포인트

### 1. similarity_search_with_score 사용

FAISS 검색 시 문서와 함께 score를 같이 반환한다.

- score는 **관측용**
- 판단 로직에는 사용하지 않음

```text
[RAG] top1 id=KB-010 score=0.12
[RAG] top2 id=KB-011 score=0.23

2. score는 로그로만 사용

threshold 없음

필터링 없음

자동 분기 없음

이유:

현재 KB 수가 적음

score의 절대값 의미를 아직 확정할 수 없음

데이터 분포를 먼저 보고 싶었기 때문

왜 score를 지금은 쓰지 않는가

FAISS similarity score는:

절대적인 기준값이 아님

문장 길이, 표현 방식, 임베딩 모델에 따라 달라짐

이 단계에서 score를 바로 기준으로 사용하면:

오히려 정상적인 KB를 버릴 가능성 존재

threshold 튜닝 근거가 없음

그래서:

지금은 “판단”보다 “관측”이 우선
```
