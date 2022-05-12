import datetime
from typing import List

from pydantic import BaseModel


class PositiveScore(BaseModel):
    __root__: float


class NewsTitle(BaseModel):
    title: str
    source: str
    pub_time: datetime.datetime
    positive: PositiveScore


class NewsTitles(BaseModel):
    __root__: List[NewsTitle]


class AveragePerDayPositiveScore(BaseModel):
    pub_date: datetime.date
    avg_positive: PositiveScore


class AveragePerDaysPositiveScore(BaseModel):
    __root__: List[AveragePerDayPositiveScore]
