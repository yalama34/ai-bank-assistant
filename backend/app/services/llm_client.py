from openai import OpenAI
from typing import Optional
from app.core.config import settings


class QwenClient:
    """Клиент для работы с Qwen в Яндекс Облаке."""

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        self.model = model or settings.get_qwen_model()
        self.temperature = temperature or settings.QWEN_TEMPERATURE
        self.max_tokens = max_tokens or settings.QWEN_MAX_TOKENS

        self._client = OpenAI(
            base_url="https://rest-assistant.api.cloud.yandex.net/v1",
            api_key=settings.YACLoud_API_KEY,
            project=settings.YACLoud_FOLDER_ID,
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Базовый вызов Qwen.
        system_prompt - попадает в instructions,
        user_prompt - в роль user.
        """
        t = temperature or self.temperature
        mt = max_tokens or self.max_tokens

        resp = self._client.responses.create(
            model=self.model,
            temperature=t,
            max_tokens=mt,
            instructions=system_prompt,
            input=[{"role": "user", "content": user_prompt}],
            store=False,
        )

        return resp.output_text