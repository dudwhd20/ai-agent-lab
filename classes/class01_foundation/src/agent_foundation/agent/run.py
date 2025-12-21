from __future__ import annotations

import sys
from agent_foundation.agent.react_agent import build_agent

def main():
    if len(sys.argv) < 2:
        print('Usage: uv run -m agent_foundation.agent.run "질문"')
        raise SystemExit(2)

    user_input = sys.argv[1]

    agent, cfg = build_agent()

    result = agent.invoke({"input": user_input}, config=cfg)
    print(result)

if __name__ == "__main__":
    main()
