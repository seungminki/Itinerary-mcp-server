from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from contextlib import asynccontextmanager


from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import json

from app.location import get_coordinate
from app.grade import get_grade
from app.prompt import SYSTEM_PROMPT
from app.schemas import Message, ChatRequest, ChatResponse, DayPlan
from settings import OPENAI_API_KEY, GOOGLE_API_KEY


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Application startup: Initializing resources...")

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)

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

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=payload.message.content),
    ]

    try:
        print(f"-> Invoking model with input: '{payload.message.content}'")
        ai_response = await model.ainvoke(messages)

        raw_response_str = ai_response.content
        print(f"<- Raw response from AI: {raw_response_str}")

        parsed_content = {}
        try:
            cleaned_str = (
                raw_response_str.strip()
                .removeprefix("```json")
                .removesuffix("```")
                .strip()
            )

            if cleaned_str:
                parsed_content = json.loads(cleaned_str)
            else:
                parsed_content = {
                    "error": "AI returned an empty response.",
                    "raw_content": raw_response_str,
                }

        except json.JSONDecodeError:
            print("⚠️ JSON parsing failed. The model did not return valid JSON.")
            parsed_content = {
                "error": "Failed to parse AI response as JSON.",
                "raw_content": raw_response_str,
            }

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": f"An internal error occurred: {str(e)}"},
        )

    parsed_content = get_coordinate(parsed_content)
    parsed_content = get_grade(parsed_content)

    return ChatResponse(
        session_id=payload.session_id,
        message=Message(role="assistant", content=parsed_content),
    )
