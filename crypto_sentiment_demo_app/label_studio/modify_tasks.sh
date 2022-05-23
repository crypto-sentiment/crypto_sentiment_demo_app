#!/bin/bash

API_KEY=$1
MODE=${2:-"import"}

docker exec -w /home/crypto_sentiment_demo_app crypto_sentiment_demo_app-label_studio \
    python3 crypto_sentiment_demo_app/label_studio/main.py \
    --mode $MODE \
    --api_key $API_KEY \
    --label_studio_url "http://127.0.0.1:8080/"
