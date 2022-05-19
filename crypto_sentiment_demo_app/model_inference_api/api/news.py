"""Pydantic data wrapper to check input types."""
from pydantic import BaseModel


class News(BaseModel):
    title: str
