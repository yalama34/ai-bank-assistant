from app.services.llm_client import QwenClient
import json


class ValidationService:
    def __init__(self):
        self.qwen = QwenClient()

    async def validate(self, original: str, answer: str) -> dict:
        system_prompt = "Ты юридический и стилистический валидатор ответов ПСБ."
        user_prompt = f"""
Проверь ответ банка на соответствие четырём критериям:
1) юридическая корректность
2) стиль
3) грамматика
4) полнота

Верни ТОЛЬКО JSON:
{{
  "legal_check": {{"passed": true/false, "issues": []}},
  "style_check": {{"passed": true/false, "issues": []}},
  "grammar_check": {{"passed": true/false, "issues": []}},
  "completeness_check": {{"passed": true/false, "issues": []}},
  "overall_score": 0-100
}}

Письмо клиента:
{original}

Ответ банка:
{answer}
"""
        raw = await self.qwen.generate(system_prompt, user_prompt)
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = {}
        if start != -1 and end > start:
            try:
                data = json.loads(raw[start:end])
            except Exception:
                data = {}
        return data