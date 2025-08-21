from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Dict, List, Optional, Any, Union


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class ScheduleItem(BaseSchema):
    order: int
    name: str
    type: str
    address: str


class DayPlan(BaseSchema):
    day: int
    schedule: List[ScheduleItem]


class Message(BaseSchema):
    role: str
    content: Union[List[DayPlan], str, None] = None


class ChatRequest(BaseSchema):
    session_id: str
    message: Message


class ChatResponse(BaseSchema):
    session_id: str
    message: Message
    tools_used: List[str] = []  # ai가 답변을 생성할 때 사용한 도구 목록
    # enhanced_context: Dict = {}  # 추가적인 맥락 정보(ex: 유저 프로필, 이전 대화 요약)
    # metadata: Dict = {}  # 부가정보: 응답 생성 시간, 토큰 사용량, 모델 버전


class ToolExecutionRequest(BaseSchema):
    tool_name: str  # 어떤 툴을 쓸건지
    parameters: Dict[str, Any]  # 파라미터 { "city": "Seoul", "date": "2025-08-18" }
    session_id: Optional[str] = None
