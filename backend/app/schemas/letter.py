from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class LetterCreate(BaseModel):
    """Схема для создания нового письма"""
    subject: str = Field(..., description="Тема письма", max_length=500)
    content: str = Field(..., description="Содержание письма")
    sender: str = Field(..., description="Отправитель", max_length=255)
    sender_email: str = Field(..., description="Email отправителя", max_length=255)
    client_id: Optional[int] = Field(None, description="ID клиента")
    correspondence_thread_id: Optional[int] = Field(None, description="ID цепочки переписки")


class LetterResponse(BaseModel):
    """Схема для ответа с данными письма"""
    id: int
    subject: str
    content: str
    sender: str
    sender_email: str
    received_at: datetime
    request_category: Optional[str] = None
    processing_params: Optional[dict] = None
    client_id: Optional[int] = None
    correspondence_thread_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

