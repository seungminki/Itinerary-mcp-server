from fastapi import FastAPI
from fastapi.responses import JSONResponse

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from schemas import ChatRequest, ChatResponse

app = FastAPI()

agent = None
prompt_messages = None


@app.on_event("startup")
async def startup():
    global agent
    global prompt_messages
    model = ChatOpenAI(model="gpt-4o-mini")

    server_connections = {
        "travelplan_recommend": {
            "transport": "streamable_http",
            "url": "http://localhost:9000/mcp",
        },
    }

    print("여러 MCP 서버에 연결 중...")
    client = MultiServerMCPClient(server_connections)
    print("연결이 설정되었습니다.")

    all_tools = await client.get_tools()
    print(f"로드된 도구: {[tool.name for tool in all_tools]}")

    agent = create_react_agent(model, all_tools)

    # --- 에이전트와 상호작용 ---
    # print("\n수학 쿼리에 대한 에이전트 호출 중...")
    # math_inputs = {"messages": [("human", "what's (3 + 5) * 12?")]}
    # math_response = await agent.ainvoke(math_inputs)
    # print("수학 응답:", math_response["messages"][-1].content)

    # print("\n날씨 쿼리에 대한 에이전트 호출 중...")
    # weather_inputs = {"messages": [("human", "뉴욕의 날씨는 어떤가요?")]}
    # weather_response = await agent.ainvoke(weather_inputs)
    # print("날씨 응답:", weather_response["messages"][-1].content)

    # print("\n호텔 정보에 대한 에이전트 호출 중...")
    # hotel_inputs = {"messages": [("human", "쏠비치 양양의 주소는 무엇인가요?")]}
    # hotel_response = await agent.ainvoke(hotel_inputs)
    # print("호텔 응답:", hotel_response["messages"][-1].content)

    # --- 예제: 프롬프트 가져오기 ---
    print("\n여행 추천 프롬프트 가져오기...")
    prompt_messages = await client.get_prompt(
        server_name="travelplan_recommend",  # connections에 정의된 이름 사용
        prompt_name="configure_assistant",
        # arguments={"skills": "기본 산수"},
    )


@app.post("/chat")
async def chat(req: ChatRequest):
    global agent
    if agent is None:
        return JSONResponse(
            status_code=503, content={"message": "Agent not initialized"}
        )

    response = await agent.ainvoke(
        {"messages": prompt_messages + [m.dict() for m in req.messages]}
    )

    final = next(
        (m for m in reversed(response["messages"]) if m.type == "ai" and m.content),
        None,
    )

    tools_used = (
        m.name for m in response["messages"] if m.type == "tool" and m.content
    )

    chat_response = ChatResponse(
        response=final.content if final else "No response",
        tools_used=tools_used,
    )

    return JSONResponse(content=chat_response.dict())
