from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from contextlib import asynccontextmanager


from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

import json

from schemas import Message, ChatRequest, ChatResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 애플리케이션 시작 프로세스를 시작합니다...")

    model = ChatOpenAI(model="gpt-4o-mini")
    server_connections = {
        "travelplan_recommend": {
            "transport": "streamable_http",
            "url": "http://172.17.0.3:9000/mcp",
        },
    }

    print("여러 MCP 서버에 연결 중...")
    client = MultiServerMCPClient(server_connections)
    print("✅ 연결이 설정되었습니다.")

    all_tools = await client.get_tools()
    print(f"🛠️ 로드된 도구: {[tool.name for tool in all_tools]}")

    prompt_messages = await client.get_prompt(
        server_name="travelplan_recommend",
        prompt_name="configure_assistant",
    )
    print("📝 기본 프롬프트를 가져왔습니다.")

    app.state.agent = create_react_agent(model, all_tools)
    app.state.prompt_messages = prompt_messages

    print("🤖 에이전트가 성공적으로 초기화되었습니다.")

    yield

    print("🧹 애플리케이션 종료 및 리소스 정리 프로세스를 시작합니다...")
    # await client.aclose()
    print("🔌 모든 연결이 안전하게 종료되었습니다.")


app = FastAPI(lifespan=lifespan)


@app.post("/chat")
async def chat(payload: ChatRequest, request: Request):
    agent = request.app.state.agent
    prompt_messages = request.app.state.prompt_messages

    if agent is None:
        return JSONResponse(
            status_code=503, content={"message": "Agent not initialized"}
        )

    response = await agent.ainvoke(
        {"messages": prompt_messages + [payload.message.model_dump()]}
    )

    final_ai_message = next(
        (m for m in reversed(response["messages"]) if m.type == "ai" and m.content),
        None,
    )

    return ChatResponse(
        session_id=payload.session_id,
        message=Message(
            role="assistant",
            content=(
                json.dumps(
                    json.loads(final_ai_message.content),
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                if final_ai_message
                else "No response"
            ),
        ),
        tools_used=[
            m.name for m in response["messages"] if m.type == "tool" and m.content
        ],
    )
