from datetime import datetime

import pandas as pd
import requests
import streamlit as st

from crypto_sentiment_demo_app.utils import get_model_inference_api_endpoint

# TODO: avoid using globals
model_api_endpoint = get_model_inference_api_endpoint()


def get_sentiment_score(n_hours: 24):
    endpoint_url = "http://data_provider:8002/positive_score/average_last_hours"
    payload = {"n": n_hours}
    result = requests.get(endpoint_url, params=payload).json()
    return result


def run_app():

    # headers
    st.title("Cryptonews sentiment")
    st.write("by Yury Kashnitsky")

    today_average_sentiment = get_sentiment_score(24)
    if not today_average_sentiment:
        today_average_sentiment = 0

    # mock version
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
        model_api_endpoint,
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
