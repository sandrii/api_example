from datetime import datetime
from pydantic import BaseModel

from api_example.app.database import Base


class BasePost(BaseModel):

    title: str
    content: str
    published: bool = True


class PostCreate(BasePost):
    pass


class Post(BasePost):

    created_at: datetime

    class Config:
        orm_mode = True
