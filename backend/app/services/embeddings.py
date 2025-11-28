from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:
    """
    Сервис генерации эмбеддингов для RAG.
    Использует SBERT-модель, указанную в настройках.
    """

    def __init__(self) -> None:
        self._model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def encode(self, texts: List[str]) -> np.ndarray:
        return self._model.encode(texts, convert_to_numpy=True)

    def encode_one(self, text: str) -> np.ndarray:
        return self.encode([text])[0]