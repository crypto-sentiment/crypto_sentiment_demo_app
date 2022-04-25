from datetime import datetime

import pandas as pd
import requests
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine.cursor import LegacyCursorResult

MODEL_API_ENDPOINT = "http://127.0.0.1:8000/classify"

# TODO move away from frontend
with open("db_connection.ini") as f:
    conn_string = f.read().strip()
    engine = create_engine(conn_string)


def get_sentiment_score(date: str = "1971-01-01"):
    query = f"""
    SELECT Avg(t1.positive)
    FROM   (model_predictions t1
        JOIN news_titles t2
          ON t1.title_id = t2.title_id)
    WHERE  date(t2.pub_time) = '{date}';
    """

    # df = pd.read_sql_query(query, con=self.sqlalchemy_engine).
    res: LegacyCursorResult = engine.execute(query)

    result: float = res.fetchone()[0]

    return result


def run_app():

    # headers
    st.title("Cryptonews sentiment")
    st.write("by Yury Kashnitsky")

    today = datetime.today().strftime("%Y-%m-%d")
    today_average_sentiment = get_sentiment_score(date=today)

    st.markdown(f"#### Today's average news sentiment: {round(today_average_sentiment * 100)}%")
    # quick n dirty
    if today_average_sentiment > 0.7:
        st.image("static/img/barometer_positive.png", width=300)
    else:
        st.image("static/img/barometer_neutral.png", width=300)

    # get user input from text areas in a Streamlit app
    title = st.text_area("Insert your title here", value="BTC drops by 10% today", height=10)

    # process input and run inference
    pred_dict = requests.post(
        MODEL_API_ENDPOINT,
        headers={"Content-Type": "application/json"},
        json={"title": title},
    ).json()

    # process predictions
    pred_df = pd.DataFrame.from_dict(pred_dict, orient="index", columns=["pred_score"]).astype(float)

    pred_df["Sentiment"] = pred_df.index
    predicted_class = pred_df["pred_score"].argmax()
    pred_class_name = pred_df.index[predicted_class]

    st.markdown(f"### Predicted class: {pred_class_name}")
    st.image(f"static/img/{pred_class_name}_icon.jpeg", width=100)

    st.markdown("Model scores for each class")
    chart_data = pred_df.copy()
    st.bar_chart(chart_data["pred_score"])


if __name__ == "__main__":
    run_app()
