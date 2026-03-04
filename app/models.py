from typing import Optional
from sqlalchemy import (
    ARRAY,
    Column,
    Integer,
    Float,
    String,
    JSON,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship, Mapped

from app.constants import MAX_NEWS
from app.database import Base


class DirtData(Base):
    __tablename__ = "dirt_data"

    news_id: Mapped[Integer] = Column(Integer, primary_key=True, index=True, unique=True)
    source: Mapped[Optional[String]] = Column(String, nullable=True, index=True)
    url_or_channel: Mapped[Optional[String]] = Column(String, nullable=True, index=True)
    text: Mapped[Optional[String]] = Column(String, nullable=True)
    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now())
    published: Mapped[DateTime] = Column(DateTime(timezone=True))

    processed_posts_rel = relationship("ProcessedPosts", back_populates="dirt_data_rel")

    def __str__(self) -> str:
        return str(f"News: {self.id}, from: {self.source}, published: {self.published}")


class ProcessedPosts(Base):
    __tablename__ = "processed_posts"

    id: Mapped[Integer] = Column(Integer, primary_key=True, index=True, unique=True)
    entities: Mapped[Optional[JSON]] = Column(JSON, nullable=True)
    embedding: Mapped[Optional[ARRAY]] = Column(ARRAY(Float), nullable=False)
    summarization: Mapped[Optional[String]] = Column(String, nullable=True)
    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now())

    news_id: Mapped[Integer] = Column(
        Integer,
        ForeignKey("dirt_data.news_id"),
        nullable=False,
        index=True,
    )
    dirt_data_rel = relationship("ProcessedPosts", back_populates="processed_posts_rel")

    def __str__(self) -> str:
        return str(f"News: {self.id}, summarization: {self.source[:MAX_NEWS]}")
