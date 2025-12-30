# Class06 – RAG score 기반 Decision Flow (LangGraph + FAISS)

Class06에서는 RAG 검색 결과의 score를 “관측 정보”가 아니라
**분기 의사결정 신호(decision signal)** 로 사용한다.

## 핵심 아이디어

- RAG top1 score를 기준으로 confidence를 3단계로 분류
  - high: 바로 안내
  - mid: 확인 질문 2개
  - low: 티켓 생성

## 흐름

User Input → RAG Search → Evaluate(score) → (high|mid|low) 분기 → 응답

## 실행

1. data/kb.jsonl 준비 (Class05 파일 복사)
2. 실행

```bash
uv run -m agent_foundation.agent.run "카카오톡 알림 안 옴"
```
