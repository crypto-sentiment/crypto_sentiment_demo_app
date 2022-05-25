#!/bin/bash

project_name="Crypto Sentiment project"
mode="import"
model_score_column_name="model_score"

while getopts ":a:p:m:c:" opt; do
    case $opt in
        a) api_key="$OPTARG";;
        p) project_name="$OPTARG";;
        m) mode="$OPTARG";;
        c) model_score_column_name="$OPTARG";;
        \?) echo "Invalid option -$OPTARG" >&2
        exit 1
        ;;
    esac

    case $OPTARG in
        -*) echo "Option $opt needs a valid argument"
        exit 1
        ;;
    esac
done

docker exec -w /home/crypto_sentiment_demo_app crypto_sentiment_demo_app-label_studio \
    python3 crypto_sentiment_demo_app/label_studio/main.py \
    --mode "$mode" \
    --project_title "$project_name" \
    --model_score_column_name "$model_score_column_name" \
    --api_key "$api_key" \
    --label_studio_url "http://127.0.0.1:8080/"
