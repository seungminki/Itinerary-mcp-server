from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent

import csv

from prompt import SYSTEM_PROMPT

mcp = FastMCP("travelplan_recommend")


def _load(csv_path: str):
    data = []
    try:
        with open(
            csv_path,
            newline="",
            encoding="utf-8",
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        return print("CSV file not found")

    print(type(data))
    return data


@mcp.tool
def fetch_restaurant():
    return _load(
        "/Users/smki/Desktop/workspace/likelion_hackathon/fastapi_likelion_hackathon/restaurant.csv"
    )


@mcp.tool
def fetch_hotel():
    return _load(
        "/Users/smki/Desktop/workspace/likelion_hackathon/fastapi_likelion_hackathon/hotel.csv"
    )


@mcp.prompt
def configure_assistant() -> list[dict]:
    # return [{"role": "system", "content": SYSTEM_PROMPT}]
    return PromptMessage(
        role="assistant", content=TextContent(type="text", text=SYSTEM_PROMPT)
    )


@mcp.prompt
def configure_user(content: str) -> str:
    return f"[컨텍스트 리셋] 이전 대화/주소 무시. '{content}'"


if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(transport="http", host="0.0.0.0", port=9000)
