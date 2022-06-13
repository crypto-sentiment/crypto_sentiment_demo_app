import os
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_health import health

from crypto_sentiment_demo_app.data_provider.db_connector import DBConnection
from crypto_sentiment_demo_app.data_provider.schemas import (
    AveragePerDaysPositiveScore,
    NewsTitles,
    PositiveScore,
)

host = os.environ.get("HOST")

if host is None:
    raise ValueError("Environment variable HOST should be defined!")

db = DBConnection()
app = FastAPI()

origins = [
    f"{host}:8000",
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_api_route("/health", health([db.is_connection_alive]))


@app.on_event("shutdown")
def db_close_connection():
    db.close_connection()


@app.get("/positive_score/average_last_hours", response_model=PositiveScore)
async def avg_positive_last_n_hours(n: int = 24):
    """Returns average positive score for news from last n hours."""
    result = db.calc_avg_positive_last_n_hours_model_predictions(n)
    return result


@app.get("/positive_score/average_per_days", response_model=AveragePerDaysPositiveScore)
async def avg_positive_per_days(start_date: str = "2022-05-01", end_date: str = "2022-05-08"):
    """
    Returns average per day positive score for news from
    (start_date <= news_publication_date <= end_date) period.
    Date format: %yyyy%-%mm%-%dd%.
    """
    result = db.calc_avg_per_day_positive_model_predictions(start_date, end_date)
    return result


@app.get("/positive_score/average_for_period", response_model=PositiveScore)
async def avg_positive_for_period(start_date: str = "2022-05-01", end_date: str = "2022-05-08"):
    """
    Returns average positive score for news from
    (start_date <= news_publication_date <= end_date) period.
    Date format: %yyyy%-%mm%-%dd%.
    """
    result = db.calc_avg_for_period_positive_model_predictions(start_date, end_date)
    return result


@app.get("/news/top_k_news_titles", response_model=NewsTitles)
async def top_k_news_titles(k: int = 10, class_name: Optional[str] = None):
    """
    Returns top-k latest model scored news filtered by class.
    Class name can be "positive", "neutral", "negative".
    If class_name is not specified the filter won't be applied.
    """
    result = db.get_top_k_news_titles(k, class_name)
    return result
