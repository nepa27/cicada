from datetime import datetime

from pydantic import BaseModel


class DirtDataCreateSchema(BaseModel):
    source: str
    url_or_channel: str
    text: str
    created_at: datetime
    published: datetime

    class Config:
        from_attributes = True


class DirtDataGetSchema(DirtDataCreateSchema):
    pass


class ProcessedPostsCreateSchema(BaseModel):
    entities: list
    embedding: list
    summarization: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessedPostsGetSchema(ProcessedPostsCreateSchema):
    pass
