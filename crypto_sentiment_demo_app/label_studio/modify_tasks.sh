#!/bin/bash

# read in the env variables defined in .env file
export $(grep -v '^#' .env | xargs -d '\n')

project_name="Crypto Sentiment project"
mode="import"
criterion="entropy"
num_samples=10
api_key=$LABEL_STUDIO_ACCESS_TOKEN
label_studio_port=$LABEL_STUDIO_PORT

while getopts ":a:p:m:c:n:s:" opt; do
    case $opt in
        a) api_key="$OPTARG";;
        p) project_name="$OPTARG";;
        m) mode="$OPTARG";;
        c) criterion="$OPTARG";;
        n) num_samples="$OPTARG";;
        s) select_top_percent="$OPTARG";;
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
    --criterion "$criterion" \
    --num_samples "$num_samples" \
    --project_title "$project_name" \
    --api_key "$api_key" \
    --label_studio_url "http://127.0.0.1:$label_studio_port/"
