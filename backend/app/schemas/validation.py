from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Результат валидации сгенерированного ответа"""
    score: int = Field(..., ge=0, le=100, description="Общий балл валидации (0-100)")
    auto_send_eligible: bool = Field(..., description="Можно ли отправить автоматически")
    legal_check: Dict[str, Any] = Field(..., description="Результаты юридической проверки")
    style_check: Dict[str, Any] = Field(..., description="Результаты проверки стиля")
    grammar_check: Dict[str, Any] = Field(..., description="Результаты проверки грамматики")
    completeness_check: Dict[str, Any] = Field(..., description="Результаты проверки полноты")
    issues: Optional[List[str]] = Field(None, description="Список найденных проблем")

