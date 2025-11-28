from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ProcessingParams(BaseModel):
    """
    Параметры обработки письма, извлеченные из анализа.
    """

    # === Классификация письма ===
    letter_type: Optional[str] = Field(
        None,
        description="Тип письма: "
                    "info_request (запрос информации/документов), "
                    "complaint (официальная жалоба или претензия), "
                    "regulatory_request (регуляторный запрос), "
                    "partnership_proposal (партнёрское предложение), "
                    "approval_request (запрос на согласование), "
                    "notification (уведомление или информирование)"
    )

    request_category: Optional[str] = Field(
        None,
        description="Категория запроса для внутренней классификации"
    )

    # === Критичные параметры обработки ===
    urgency: Optional[str] = Field(
        None,
        description="Срочность ответа: low/medium/high/critical"
    )

    sla_deadline: Optional[datetime] = Field(
        None,
        description="Автоматически вычисленный дедлайн на основе типа запроса и нормативных требований"
    )

    formality_level: Optional[str] = Field(
        None,
        description="Уровень формальности тона: "
                    "strict_official (строгий официальный), "
                    "corporate (деловой корпоративный), "
                    "client_oriented (клиентоориентированный), "
                    "brief (краткий информационный)"
    )

    approval_departments: List[str] = Field(
        default_factory=list,
        description="Список подразделений, требующих согласования ответа"
    )

    legal_risks: Optional[str] = Field(
        None,
        description="Уровень юридических рисков: none/low/medium/high"
    )

    # === Извлеченная ключевая информация ===
    request_essence: Optional[str] = Field(
        None,
        description="Суть запроса - точное определение предмета обращения"
    )

    contact_info: Optional[Dict[str, Any]] = Field(
        None,
        description="Структурированные контактные данные и реквизиты отправителя"
    )

    regulatory_references: List[str] = Field(
        default_factory=list,
        description="Ссылки на нормативные акты, упомянутые в письме"
    )

    sender_expectations: Optional[str] = Field(
        None,
        description="Требования и ожидания отправителя"
    )

    # === Параметры для генерации ответа ===
    response_style: Optional[str] = Field(
        None,
        description="Стиль ответа: "
                    "strict_official (для регуляторов и госорганов), "
                    "corporate (для партнёров и контрагентов), "
                    "client_oriented (для физ/юр лиц), "
                    "brief (для простых запросов)"
    )

    requires_response: bool = Field(
        True,
        description="Требуется ли ответ на письмо (уведомления могут не требовать)"
    )

    # === Контекстуальная адаптация ===
    relationship_level: Optional[str] = Field(
        None,
        description="Уровень отношений с отправителем: "
                    "regulator (регулятор), "
                    "government (госорган), "
                    "partner (партнёр), "
                    "corporate_client (корпоративный клиент), "
                    "individual_client (физлицо), "
                    "counterparty (контрагент)"
    )

    client_type: Optional[str] = Field(
        None,
        description="Тип клиента: individual/corporate/government/regulator/partner"
    )

    # === Дополнительные параметры для маршрутизации ===
    operation_amount: Optional[float] = Field(
        None,
        description="Сумма операции (если упомянута в письме)"
    )

    document_type: Optional[str] = Field(
        None,
        description="Тип документа: contract/amendment/application/statement/other"
    )

    change_type: Optional[str] = Field(
        None,
        description="Критичность изменения: normal/substantial/critical"
    )

    geography: Optional[str] = Field(
        None,
        description="Регион/страна отправителя"
    )

    # === Параметры для согласования ===
    requires_legal_review: bool = Field(
        False,
        description="Требуется ли обязательный юридический просмотр"
    )

    requires_top_management: bool = Field(
        False,
        description="Требуется ли участие топ-менеджмента"
    )

    compliance_notes: Optional[str] = Field(
        None,
        description="Заметки по compliance и внутренним политикам"
    )

    # === Метаданные обработки ===
    processing_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Дополнительные метаданные, извлеченные при анализе"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "letter_type": "regulatory_request",
                "urgency": "high",
                "formality_level": "strict_official",
                "approval_departments": ["legal", "compliance", "risk"],
                "legal_risks": "high",
                "response_style": "strict_official",
                "relationship_level": "regulator",
                "requires_legal_review": True,
                "sla_deadline": "2024-12-31T23:59:59"
            }
        }