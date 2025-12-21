# agent-foundation (Step 1)

## 목표

- ReAct 루프 기반으로 Tool을 호출하는 단일 Agent 구축
- Tool Schema를 계약서 수준으로 정의(Pydantic args_schema)
- Tool 호출 감사로그(JSONL)로 재현 가능한 실행 이력 확보

## Tools

- search_kb(query, top_k) -> KB 문서 리스트
- create_ticket(title, description, priority) -> ticket_id 등 반환

## Run

1. 의존성 설치

- uv 사용 시: uv sync
- pip 사용 시: pip install -e .

2. 환경변수 설정

- .env.example 참고해서 .env 생성

3. 실행

```bash
python -m agent.run "VPN이 갑자기 접속이 안돼요. 뭐부터 확인하죠?"
```
