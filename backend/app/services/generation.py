from typing import Optional, Dict, Any, List

from app.services.llm_client import QwenClient
from app.services.vector_db import VectorDBService
from app.services.system_prompts import GenerationPrompts
from app.utils.run_parser import run_parser


class GenerationService:
    """
    Генерация ответа с учётом стиля и RAG-контекста (похожие прецеденты).
    """

    def __init__(self) -> None:
        self.qwen = QwenClient()
        self.vector_db = VectorDBService()

    async def generate_response(
        self,
        letter_text: str,
        style: GenerationPrompts,
        extra_context: dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
        k: int = 3,
    ) -> dict[str, Any]:
        """
        Генерация ответа.

        letter_text: исходное письмо клиента
        style: стиль ответа (enum)
        extra_context: дополнительный контекст (история переписки и т.п.)
        filters: фильтры для поиска прецедентов в Qdrant
        k: сколько прецедентов подтянуть
        """
        #Поиск похожих прецедентов
        precedents: List[Dict[str, Any]] = self.vector_db.search_similar(
            query_text=letter_text,
            limit=k,
            filters=filters,
        )

        precedents_block = ""
        if precedents:
            lines: List[str] = ["Похожие прецеденты (для ориентира, не копируй дословно):"]
            for i, item in enumerate(precedents, start=1):
                inc = item["incoming_text"][:300]
                ans = item["answer_text"][:300]
                lines.append(
                    f"\nПрецедент {i}:\nВходящее письмо:\n{inc}\nОтвет банка ПСБ:\n{ans}\n"
                )
            precedents_block = "\n".join(lines)

        #Сбор промпта
        system_prompt = style.value
        user_parts = []
        if extra_context:
            user_parts.append(f"Дополнительный контекст:\n{extra_context}\n")
        if precedents_block:
            user_parts.append(precedents_block + "\n")

        user_parts.append(f"Письмо клиента:\n{letter_text}\n")
        user_parts.append("Сформируй ответ в соответствии с инструкциями системного промпта.")

        user_prompt = "\n".join(user_parts)

        return {
            "answer": await self.qwen.generate(system_prompt, user_prompt),
            "style": style
        }