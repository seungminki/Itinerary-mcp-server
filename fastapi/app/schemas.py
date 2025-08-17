from pydantic import BaseModel
from typing import Dict, List, Optional, Any


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    # session_id: Optional[str]
    messages: list[Message]


class ChatResponse(BaseModel):
    response: str
    # session_id: str
    tools_used: List[str] = []  # ai가 답변을 생성할 때 사용한 도구 목록
    # enhanced_context: Dict = {}  # 추가적인 맥락 정보(ex: 유저 프로필, 이전 대화 요약)
    # metadata: Dict = {}  # 부가정보: 응답 생성 시간, 토큰 사용량, 모델 버전


class ToolExecutionRequest(BaseModel):
    tool_name: str  # 어떤 툴을 쓸건지
    parameters: Dict[str, Any]  # 파라미터 { "city": "Seoul", "date": "2025-08-18" }
    session_id: Optional[str] = None
