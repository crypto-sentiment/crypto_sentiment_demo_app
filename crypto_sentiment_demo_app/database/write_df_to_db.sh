#!/bin/bash

index_col_name=title_id
docker_container=crypto_sentiment_demo_app-crawler-1

while getopts ":p:t:i:" opt; do
    case $opt in
        p) path_to_csv="$OPTARG";;
        t) table_name="$OPTARG";;
        i) index_col_name="$OPTARG";;
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

docker cp $path_to_csv $docker_container:/root/data

docker exec $docker_container \
    python3 crypto_sentiment_demo_app/database/write_df_to_db.py \
    --path_to_csv /root/data/"$(basename -- $path_to_csv)" \
    --table_name "$table_name" \
    --index_col_name "$index_col_name"
