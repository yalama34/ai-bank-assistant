import json
from typing import Any, Dict

from app.services.llm_client import QwenClient
from app.services.vector_db import VectorDBService


class AnalysisService:
    """
    Анализ входящего письма:
    - поиск похожих прецедентов (RAG);
    - классификация и извлечение параметров через Qwen.
    """

    def __init__(self) -> None:
        self.qwen = QwenClient()
        self.vector_db = VectorDBService()

    async def analyze_letter(self, letter_text: str) -> Dict[str, Any]:
        # Поиск похожих прецедентов
        similar = self.vector_db.search_similar(letter_text, limit=5)

        # Сбор контекста
        precedents_block = ""
        if similar:
            parts = []
            for i, item in enumerate(similar, start=1):
                inc = item["incoming_text"][:300]
                ans = item["answer_text"][:300]
                parts.append(
                    f"Прецедент {i}:\nВходящее:\n{inc}\nОтвет банка:\n{ans}\n"
                )
            precedents_block = "\n\nПохожие прецеденты:\n" + "\n".join(parts)

        # Qwen анализирует и выдает JSON
        system_prompt = "Ты аналитик ПСБ. Классифицируй письмо и верни только JSON."
        user_prompt = f"""
Проанализируй письмо клиента и верни JSON с параметрами обработки.

Поля JSON:
- request_category
- urgency
- formality_level
- approval_departments (список строк)
- legal_risks
- operation_amount (число или null)
- client_type
- document_type
- change_type
- geography

Если информации для какого‑то поля недостаточно, ставь null или пустой список.

{precedents_block}

Письмо клиента:
{letter_text}
"""
        raw = await self.qwen.generate(system_prompt, user_prompt)

        start = raw.find("{")
        end = raw.rfind("}") + 1
        params: Dict[str, Any] = {}
        if start != -1 and end > start:
            try:
                params = json.loads(raw[start:end])
            except Exception:
                params = {}

        return {
            "processing_params": params,
            "request_category": params.get("request_category"),
            "similar_precedents": similar,
        }


