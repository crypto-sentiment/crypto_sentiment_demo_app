import datetime
from typing import Optional

import sqlalchemy as db
from sqlalchemy.exc import SQLAlchemyError

from crypto_sentiment_demo_app.utils import get_db_connection_engine
from crypto_sentiment_demo_app.data_provider.schemas import ClassesMapping


class DBConnection:
    """
    A class for retrieving all necessary information from
    our PostgreSQL database to our frontend.


    Attributes
    ----------
    engine : sqlalchemy.engine.base.Engine
        SQLAlchemy Engine
    conn : sqlalchemy.engine.base.Connection
        SQLAlchemy Connection
    metadata : sqlalchemy.sql.schema.MetaData
        Metadata of our PostgreSQL database
    news_titles : sqlalchemy.sql.schema.Table
        news_titles table representation
    model_predictions : sqlalchemy.sql.schema.Table
        model_predictions table representation

    Methods
    -------
    close_connection():
        Fully closing all database connections.

    _create_table_obj(table_name):
        Creates table representation.

    _construct_query_template(selectables, class_name):
        Returns query boilerplate with selected columns
        from selectables and join operators.

    _filter_by_predicted_class(query, class_name)
        Filters news by predicted class.

    _execute_and_fetchall(query):
        Executes query and fetches the result.

    get_top_k_news_titles(k, class_name):
        Returns top-k latest model scored news.

    calc_avg_positive_last_n_hours_model_predictions(n_hours):
        Returns average positive score for news from last n hours.

    calc_avg_per_day_positive_model_predictions(start_date, end_date):
        Returns average per day positive score for news from
        (start_date <= news_publication_date <= end_date) period.
        Date format: %yyyy%-%mm%-%dd%.

    calc_avg_period_positive_model_predictions(start_date, end_date):
        Returns average positive score for news from
        (start_date <= news_publication_date <= end_date) period.
        Date format: %yyyy%-%mm%-%dd%.
    """

    def __init__(self):
        """Constructs all the necessary attributes."""
        self.engine = get_db_connection_engine()
        self.conn = self.engine.connect()
        self.metadata = db.MetaData()
        self.news_titles = self._create_table_obj("news_titles")
        self.model_predictions = self._create_table_obj("model_predictions")

    def is_connection_alive(self) -> bool:
        test_query = db.select(db.text("1"))
        try:
            self._execute_and_fetchall(test_query)
            return True
        except SQLAlchemyError:
            return False

    def close_connection(self):
        """Fully closing all database connections."""
        self.conn.close()
        self.engine.dispose()

    def _create_table_obj(self, table_name: str) -> db.sql.schema.Table:
        """Creates table representation."""
        return db.Table(table_name, self.metadata, autoload=True, autoload_with=self.engine)

    def _construct_query_template(self, selectables: list, class_name: Optional[str] = None) -> db.sql.selectable.Select:
        """
        Returns query boilerplate with selected columns
        from selectables and join operators.
        """
        join_query = self.news_titles.join(
            right=self.model_predictions,
            onclause=self.news_titles.c.title_id == self.model_predictions.c.title_id,
        )
        template = db.select(selectables).select_from(join_query)
        return self._filter_by_predicted_class(template, class_name)

    def _filter_by_predicted_class(self, query: db.sql.selectable.Select, class_name: Optional[str] = None) -> db.sql.selectable.Select:
        """Filters news by predicted class."""
        predicted_class = self.model_predictions.c.predicted_class
        if class_name in ClassesMapping.__members__:
            class_filter = predicted_class == ClassesMapping[class_name].value
        else:
            class_filter = predicted_class != None
        return query.filter(class_filter)

    def _execute_and_fetchall(self, query: db.sql.selectable.Select) -> list:
        """Executes query and fetches the result."""
        result = self.conn.execute(query)
        return result.fetchall()

    def get_top_k_news_titles(self, k: int, class_name: Optional[str] = None) -> list:
        """Returns top-k latest model scored news."""
        selectables = [
            self.news_titles.c.title,
            self.news_titles.c.source,
            self.news_titles.c.pub_time,
            self.model_predictions.c.positive,
        ]
        query_template = self._construct_query_template(
            selectables, class_name)
        query = query_template.order_by(
            self.news_titles.c.pub_time.desc()).limit(k)
        return self._execute_and_fetchall(query)

    def calc_avg_positive_last_n_hours_model_predictions(self, n_hours: int) -> Optional[float]:
        """Returns average positive score for news from last n hours."""
        datetime_mark = datetime.datetime.now() - datetime.timedelta(hours=n_hours)
        selectables = [db.func.avg(self.model_predictions.c.positive)]
        query_template = self._construct_query_template(selectables)
        query = query_template.where(
            self.news_titles.c.pub_time >= datetime_mark)
        return self._execute_and_fetchall(query)[0][0]

    def calc_avg_per_day_positive_model_predictions(self, start_date: str, end_date: str) -> list:
        """
        Returns average per day positive score for news from
        (start_date <= news_publication_date <= end_date) period.
        Date format: %yyyy%-%mm%-%dd%.
        """
        pub_date_col = db.cast(self.news_titles.c.pub_time, db.Date)
        selectables = [
            pub_date_col.label("pub_date"),
            db.func.avg(self.model_predictions.c.positive).label(
                "avg_positive"),
        ]
        query_template = self._construct_query_template(selectables)
        query = (
            query_template.filter(pub_date_col.between(start_date, end_date))
            .group_by(pub_date_col)
            .order_by(pub_date_col.desc())
        )
        return self._execute_and_fetchall(query)

    def calc_avg_for_period_positive_model_predictions(self, start_date: str, end_date: str) -> Optional[float]:
        """
        Returns average positive score for news from
        (start_date <= news_publication_date <= end_date) period.
        Date format: %yyyy%-%mm%-%dd%.
        """
        pub_date_col = db.cast(self.news_titles.c.pub_time, db.Date)
        selectables = [db.func.avg(
            self.model_predictions.c.positive).label("avg_positive")]
        query_template = self._construct_query_template(selectables)
        query = query_template.filter(
            pub_date_col.between(start_date, end_date))
        return self._execute_and_fetchall(query)[0][0]


if __name__ == '__main__':
    db_conn = DBConnection()
    print(db_conn.get_top_k_news_titles(10))
