from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

from .processing_params import ProcessingParams


class LetterCreate(BaseModel):
    subject: str
    content: str
    sender: str
    sender_email: EmailStr
    client_id: Optional[int] = None
    correspondence_thread_id: Optional[int] = None


class DraftResponse(BaseModel):
    id: int
    letter_id: int
    content: str
    style: Optional[str] = None
    validation_score: Optional[int] = None
    validation_result: Optional[dict] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApprovalResponse(BaseModel):
    id: int
    letter_id: int
    draft_id: Optional[int] = None
    route: Optional[dict] = None
    current_approver: Optional[str] = None
    approval_status: Optional[str] = None
    operation_amount: Optional[float] = None
    request_category: Optional[str] = None
    department: Optional[str] = None
    risk_level: Optional[str] = None
    geography: Optional[str] = None
    client_type: Optional[str] = None
    document_type: Optional[str] = None
    change_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LetterResponse(BaseModel):
    id: int
    subject: str
    content: str
    sender: str
    sender_email: str
    received_at: datetime
    request_category: Optional[str] = None
    processing_params: Optional[ProcessingParams] = None
    client_id: Optional[int] = None
    correspondence_thread_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    drafts: List[DraftResponse] = []
    approvals: List[ApprovalResponse] = []

    class Config:
        from_attributes = True

