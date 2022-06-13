import os

from minio import Minio
from minio.error import S3Error


def main():
    # Create a client with the MinIO server connection
    client = Minio(
        os.getenv("MLFLOW_S3_ENDPOINT_URL").split("/")[-1],
        access_key=os.getenv("AWS_ACCESS_KEY_ID"),
        secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        secure=False,
    )

    bucket_name = os.getenv("AWS_S3_BUCKET")

    # Make bucket if not exist.
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
    else:
        print(f"Bucket '{bucket_name}' already exists")


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)
