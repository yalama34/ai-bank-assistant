from app.services.llm_client import QwenClient
import json
from typing import Any


class ValidationService:
    def __init__(self):
        self.qwen = QwenClient()

    async def validate(self, original: str, result: dict[str, Any]) -> dict:
        answer = result["answer"]
        style = result["style"]
        style_prompt = style.value
        system_prompt = "Ты юридический и стилистический валидатор ответов ПСБ."
        user_prompt = f"""
Проверь ответ банка на соответствие четырём критериям:
1) юридическая корректность: все использованные в ответе на письмо законы/НПА соответствуют контексту и не выходят за его рамки
2) стиль: соответствие выбранному стилю общения между потребителем и клиентом
3) грамматика: проверка ответа банка на грамматические ошибки
4) полнота: ответ должен быть окончательным, информативным и понятным, поставленный вопрос должен быть закрытым, если были предоставлены все данные для
закрытия вопроса. Если же таких данных не предоставлено, то убери критерий того, что ответ должен быть окончательным

Верни ТОЛЬКО JSON:
{{
  "legal_check": {{"passed": true/false, "issues": []}},
  "style_check": {{"passed": true/false, "issues": []}},
  "grammar_check": {{"passed": true/false, "issues": []}},
  "completeness_check": {{"passed": true/false, "issues": []}},
  "overall_score": 0-100
}}

Пояснения к параметрам JSON:
issues должен содержать причину почему проверка по критерию провалена. Указывай её максимально кратко
overall_score - общая оценка ответа. Влияние на score в порядке убывания: legal_check, grammar_check, completion_ckeck, style_check

Письмо клиента:
{original}

Ответ банка:
{answer}

Выбранный моделью стиль: {style}

Промпт, соответствующий стилю:
{system_prompt}
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