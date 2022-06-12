#!/bin/sh

# Create bucket in minio (if it doesn't exist yet)
python3 create_bucket.py

# Run MLflow server
mlflow server \
    --backend-store-uri postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/${POSTGRES_DB} \
    --default-artifact-root s3://${AWS_S3_BUCKET}/ \
    --host 0.0.0.0
