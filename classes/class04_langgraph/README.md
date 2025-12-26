# Class04 – LangGraph 기반 Agent Flow 구성

Class04에서는 기존 if/else 또는 ReAct 스타일 Agent를 벗어나  
**LangGraph(State Graph)** 를 사용해  
에이전트의 실행 흐름을 구조적으로 표현했다.

핵심은 “LLM이 무엇을 할지”보다  
**시스템이 어떤 흐름으로 움직이는지**를 명확히 하는 것이었다.

---

## 무엇을 해봤나

### 1. Agent 실행 흐름을 그래프로 모델링

Agent의 전체 동작을 노드와 엣지로 표현했다.

- 분기 조건이 코드로 명확
- 흐름이 한눈에 보임
- 노드 단위로 수정 및 확장 가능

---

### 2. State 중심 설계

Agent 실행 중 사용하는 모든 정보는 `AgentState` 하나로 관리했다.

```python
class AgentState(BaseModel):
    user_text: str
    kb_query: str
    kb_hits: list
    action: str
    ticket: dict | None
    final_text: str
```

3. LLM 역할 제한

LLM은 다음 역할만 수행하도록 제한했다.

KB 검색 결과가 있을 때 → 점검 가이드 문장 생성

티켓이 생성되었을 때 → 티켓 안내 문장 생성

판단 로직은 모두 코드에서 처리했다.

검색

분기

티켓 생성 여부

LLM은 결정자가 아니라 출력 생성기로만 사용했다.

4. 키워드 기반 KB 검색의 한계 확인

Class04-A에서는 단순 KB 검색 로직을 사용했으며,
다음과 같은 한계를 명확히 확인했다.

의미 없는 문장에도 KB가 매칭되는 오탐

부분 문자열 기반 매칭의 한계

이를 통해:

임베딩 기반 RAG의 필요성을 명확히 인식

다음 단계(Class05)의 방향을 자연스럽게 설정할 수 있었다.

실행 예시

uv run -m agent_foundation.agent.run "카카오톡 알림 안 옴"

이 단계에서 느낀 점

Agent 품질보다 구조 설계가 먼저라는 감각이 확실해졌다.

LangGraph는 성능을 올려주기보다는
시스템을 망가지지 않게 만드는 도구라는 인상이 강했다.

멀티 에이전트나 Supervisor 구조로 확장하기 좋은 기반이었다.

```

```
