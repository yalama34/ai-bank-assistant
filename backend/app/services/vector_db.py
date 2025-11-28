from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.core.config import settings
from app.services.embeddings import EmbeddingService


class VectorDBService:
    """
    Обёртка над Qdrant для RAG.
    Хранит прецеденты (письмо + ответ + метаданные) и позволяет искать похожие кейсы.
    """

    def __init__(self) -> None:
        self._client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
        self._collection = settings.QDRANT_COLLECTION_NAME
        self._embeddings = EmbeddingService()
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Создаёт коллекцию, если её нет."""
        collections = self._client.get_collections().collections
        names = {c.name for c in collections}
        if self._collection not in names:
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                ),
            )

    def index_precedent(
        self,
        incoming_text: str,
        answer_text: str,
        metadata: Optional[Dict[str, Any]] = None,
        point_id: Optional[str] = None,
    ) -> str:
        """
        Индексирует один прецедент.
        incoming_text + answer_text -> единый вектор.
        """
        import uuid

        meta = metadata or {}
        pid = point_id or str(uuid.uuid4())
        combined = f"Входящее письмо:\n{incoming_text}\n\nОтвет банка:\n{answer_text}"
        vec = self._embeddings.encode_one(combined)

        self._client.upsert(
            collection_name=self._collection,
            points=[
                PointStruct(
                    id=pid,
                    vector=vec.tolist(),
                    payload={
                        "incoming_text": incoming_text,
                        "answer_text": answer_text,
                        **meta,
                    },
                )
            ],
        )
        return pid

    def search_similar(
        self,
        query_text: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Ищет похожие прецеденты по тексту запроса.

        filters — опциональный словарь для фильтрации по payload (например, {"request_category": "complaint"}).
        """
        vec = self._embeddings.encode_one(query_text)

        q_filter = None
        if filters:
            conditions = []
            for key, val in filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=val),
                    )
                )
            q_filter = Filter(must=conditions)

        results = self._client.search(
            collection_name=self._collection,
            query_vector=vec.tolist(),
            limit=limit,
            query_filter=q_filter,
        )

        out: List[Dict[str, Any]] = []
        for r in results:
            payload = r.payload or {}
            out.append(
                {
                    "score": r.score,
                    "incoming_text": payload.get("incoming_text", ""),
                    "answer_text": payload.get("answer_text", ""),
                    "metadata": {k: v for k, v in payload.items() if k not in ("incoming_text", "answer_text")},
                }
            )
        return out


