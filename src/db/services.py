from datetime import datetime
from typing import Type

from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession


from src.base.crud_base import CRUDBase
from src.base.models import Base


class DirtDataService:
    """Обрабатывает сырые данные."""

    def __init__(
            self,
            session: AsyncSession,
            model: Type[Base],
            schema: Type[BaseModel],
            data: list
    ) -> None:
        self.session = session
        self.crud = CRUDBase(model, self.session)
        self.schema = schema
        self.data = data

    async def insert_data(self) -> None:
        """Добавляет сырые данные в БД."""
        for item in self.data:
            # Избавиться от указания конкретных полей
            item["created_at"] = await self.parse_iso_datetime(item["created_at"])
            item["published"] = await self.parse_iso_datetime(item["published"])
            schema = self.schema(**item)
            await self.crud.create(schema.model_dump())

    @staticmethod
    async def parse_iso_datetime(iso_str: str) -> datetime:
        """Преобразует ISO строку в datetime с timezone."""
        if iso_str.endswith('Z'):
            iso_str = iso_str[:-1] + '+00:00'
        return datetime.fromisoformat(iso_str)
