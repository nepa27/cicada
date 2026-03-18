import asyncio
from datetime import datetime
from typing import Type, Sequence, Any

from pydantic import ValidationError
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances
from spacy import Language
from sqlalchemy.ext.asyncio import AsyncSession

from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer
from torch import Tensor

from src.base.crud_base import CRUDBase
from src.base.models import Base
from src.config.decorators import logger
from src.db.models import ProcessedPosts
from src.schemas.schemas import ProcessedPostsCreateSchema


class ProcessedPostsService:
    """Обогащает сырые данные(ML-обработка)."""

    TOKENIZER = "russian"
    MAX_SIZE_TEXT = 500
    CUT_TEXT = 300
    SIZE_OF_SENTENCE = 4

    def __init__(
            self,
            session: AsyncSession,
            model: Type[Base],
            nlp_model: Language,
            st_model: SentenceTransformer
    ) -> None:
        self.session = session
        self.crud = CRUDBase(model, self.session)
        self.nlp_model = nlp_model
        self.st_model = st_model

    async def get_ner(self, text: str) -> list:
        entities: list = []
        document = self.nlp_model(self.get_preview(text))
        for ent in document.ents:
            entities.append(str(ent))
        # numbers = [token.text for token in document if token.like_num]
        # print("Найденные числа в первом тексте:", numbers)
        return entities

    async def get_embedding(self, text: str) -> Tensor:
        return self.st_model.encode(text)

    def get_preview(self, text) -> str:
        if len(text) > ProcessedPostsService.MAX_SIZE_TEXT:
            preview = self.extractive_summary(
                text,
                sentences_count=ProcessedPostsService.SIZE_OF_SENTENCE
            )
        else:
            preview = text[:ProcessedPostsService.CUT_TEXT]

        return preview

    # TODO: позже исправить! Перейти от агломеративной кластеризации к инкрементальной
    @staticmethod
    async def get_clastes(embeddings: tuple) -> list:
        distances = cosine_distances(embeddings)

        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=0.3,
            metric='precomputed',
            linkage='average'
        )
        clustering.fit(distances)
        labels = clustering.labels_
        return labels

    @staticmethod
    def extractive_summary(text: str, sentences_count: int) -> str:
        parser = PlaintextParser.from_string(
            text,
            Tokenizer(ProcessedPostsService.TOKENIZER)
        )
        summarizer = TextRankSummarizer()
        summary = summarizer(parser.document, sentences_count)
        return ' '.join(str(sentence) for sentence in summary)

    async def insert_processed_posts(self, data: Sequence[Any]):
        tasks_emb = [self.get_embedding(dt.text) for dt in data]
        embeddings = await asyncio.gather(*tasks_emb)
        tasks_ner = [self.get_ner(dt.text) for dt in data]
        ner = await asyncio.gather(*tasks_ner)

        processed_posts = []
        for i, (dt, emb, n, c) in enumerate(zip(data, embeddings, ner)):
            try:
                processed_post_data = ProcessedPostsCreateSchema(
                    entities=n,
                    embedding=emb.tolist(),
                    summarization=dt.text,
                    created_at=datetime.now()
                )
                processed_post = ProcessedPosts(
                    entities=processed_post_data.entities,
                    embedding=processed_post_data.embedding,
                    summarization=processed_post_data.summarization,
                    news_id=dt.news_id,
                    created_at=processed_post_data.created_at
                )
                processed_posts.append(processed_post)
            except ValidationError as e:
                logger.error(f'Ошибка валидации: {e}')
                raise
        try:
            self.session.add_all(processed_posts)
            await self.session.commit()
        except Exception as e:
            logger.error(f'Ошибка при добавлении данных в БД: {e}')
            await self.session.rollback()