import logging
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.core.config import settings
from app.services.embeddings import EmbeddingService

from ..utils.run_parser import run_parser

logger = logging.getLogger(__name__)


class VectorDBService:
    """
    Обёртка над Qdrant для RAG.
    Хранит прецеденты (письмо + ответ + метаданные) и позволяет искать похожие кейсы.
    """

    def __init__(self) -> None:
        self._client: Optional[QdrantClient] = None
        self._collection = settings.QDRANT_COLLECTION_NAME
        self._embeddings = EmbeddingService()
        self._connect()
        self.added = False
        self.add_faq_to_RAG()

    def _connect(self) -> None:
        """Инициализирует подключение к Qdrant, но не валит приложение, если сервис недоступен."""
        if not settings.QDRANT_HOST:
            logger.warning("QDRANT_HOST не задан, RAG будет отключён")
            return

        try:
            self._client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
            )
            self._ensure_collection()
        except Exception as exc:
            logger.warning(
                "Не удалось подключиться к Qdrant (%s:%s): %s. Продолжаем работу без RAG.",
                settings.QDRANT_HOST,
                settings.QDRANT_PORT,
                exc,
            )
            self._client = None

    def _ensure_collection(self) -> None:
        """Создаёт коллекцию, если её нет."""
        if not self._client:
            return

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
    def add_faq_to_RAG(self):
        if not self.added:
            return
        sorted_cats = run_parser()
        loaded = 0
        for cat, faqs in sorted_cats:
            for faq in faqs:
                try:
                    question = faq.get("question")
                    answer = faq.get("answer")
                    if not question or not answer:
                        continue
                    metadata = {
                        "doc_type": "faq",
                        "source": faq.get("source", "unknown"),
                        "url": faq.get("url", ""),
                        "category": faq.get("category", ""),
                    }
                    self.index_precedent(
                        incoming_text=f"Вопрос: {question}",
                        answer_text=f"Ответ: {answer}",
                        metadata=metadata,
                    )
                    loaded += 1
                except Exception as e:
                    print(e)
                    print(faq)
        self.added = True

        print(f"Загружено {loaded} FAQ в коллекцию {self._collection}")
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

        if not self._client:
            raise RuntimeError("Подключение к Qdrant недоступно, индексировать данные нельзя")

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
        if not self._client:
            logger.info("Qdrant недоступен, возвращаем пустой список прецедентов")
            return []

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

        results = self._client.query_points(
            collection_name=self._collection,
            query=vec.tolist(),
            limit=limit,
            query_filter=q_filter,

        )

        out: List[Dict[str, Any]] = []
        for r in results:
            point_id, score = r
            point_id, score = r
            incoming = ""
            answer = ""
            meta = {}

            out.append(
                {
                    "score": score,
                    "incoming_text": incoming,
                    "answer_text": answer,
                    "metadata": meta,
                }
            )

        return out









