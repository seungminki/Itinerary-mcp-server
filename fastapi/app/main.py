from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from contextlib import asynccontextmanager


from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

import json

from app.location import get_coordinate
from app.grade import get_grade
from app.db import get_output_db
from app.prompt import SYSTEM_PROMPT
from app.schemas import Message, ChatRequest, ChatResponse, AiDayPlanListResponse
from settings import OPENAI_API_KEY, GOOGLE_API_KEY


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Application startup: Initializing resources...")

    model = ChatOpenAI(
        model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY
    ).with_structured_output(AiDayPlanListResponse, method="function_calling")

    app.state.model = model
    print("✅ AI model initialized and stored successfully.")

    yield

    print("🧹 Application shutdown: Cleaning up resources...")
    app.state.model = None
    print("🔌 Resources released.")


app = FastAPI(lifespan=lifespan)


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request):
    model = request.app.state.model
    if not model:
        return JSONResponse(
            status_code=503,
            content={
                "message": "Service Unavailable: The AI model is not initialized."
            },
        )

    print(f"-> Invoking model with input: '{payload.message.content}'")
    db_result = get_output_db(payload.message.content)

    if db_result:

        print(f"<- Raw response from AI, DB: {db_result}")
        return ChatResponse(
            session_id=payload.session_id,
            message=Message(role="assistant", content=db_result),
        )

    else:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=payload.message.content),
        ]

        try:
            ai_response = await model.ainvoke(messages)
            raw_response_str = ai_response.model_dump()["plans"]
            print(f"<- Raw response from AI: {raw_response_str}")

        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            return JSONResponse(
                status_code=500,
                content={"message": f"An internal error occurred: {str(e)}"},
            )

        raw_response_str = get_coordinate(raw_response_str)
        raw_response_str = get_grade(raw_response_str)

        return ChatResponse(
            session_id=payload.session_id,
            message=Message(role="assistant", content=raw_response_str),
        )
