from typing import Type, TypeVar, Sequence, Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.sql import text

from src.base.models import Base
from src.config.decorators import logger


ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


class CRUDBase:
    """Универсальный базовый класс для CRUD операций."""

    def __init__(self, model: Type[Base], session: AsyncSession):
        """
        Инициализирует CRUD-класс с указанной моделью.

        Параметры:
            model: SQLAlchemy-модель (класс), связанный с таблицей в БД.
        """
        self.model = model
        self.session = session

    async def get_all(self) -> Sequence[Any]:
        """Получает данные из БД."""
        query = await self.session.execute(select(self.model))
        return query.scalars().all()

    async def get_one_or_none(self, obj_id: int) -> ModelType | None:
        """Получает объект из БД по id или выбрасывает 404-ошибку."""
        query = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return query.scalar_one_or_none()

    async def create(self, data: CreateSchemaType) -> ModelType:
        """Добавляет данные в БД."""
        db_obj = self.model(**data)
        try:
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(db_obj)

            return db_obj
        except Exception as e:
            logger.error(f'Ошибка при добавлении данных в БД: {e}')
            await self.session.rollback()

    async def update(self, data: dict, obj_id: int) -> None:
        """Обновляет данные в БД."""
        try:
            query = (
                update(self.model)
                .values(**data)
                .filter_by(id=obj_id)
            )
            await self.session.execute(query)
            await self.session.commit()
        except Exception as e:
            logger.error(f'Ошибка при обновлении данных в БД: {e}')
            await self.session.rollback()

    @staticmethod
    async def delete(db_object: Base, session: AsyncSession) -> None:
        """Удаляет данные из БД."""
        try:
            await session.delete(db_object)
            await session.commit()
        except Exception as e:
            logger.error(f'Ошибка при удалении данных в БД: {e}')
            await session.rollback()

    @staticmethod
    async def check_db_connection(engine: AsyncEngine) -> None:
        try:
            async with engine.connect() as connection:
                result = await connection.execute(text('SELECT version();'))
                db_version = result.scalar_one()
                logger.info(f'База данных подключена. Версия: {db_version}')
        except Exception as e:
            logger.info(f'Ошибка при подключении к БД: {e}')

    @staticmethod
    async def create_tables(engine: AsyncEngine) -> None:
        """Функция создания таблиц."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def delete_tables(engine: AsyncEngine) -> None:
        """Функция удаления таблиц."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
