import argparse

import pandas as pd

from crypto_sentiment_demo_app.label_studio.data import (
    read_data_from_db,
    write_data_to_db,
)
from crypto_sentiment_demo_app.label_studio.label_studio import LabelStudioProject
from crypto_sentiment_demo_app.label_studio.sampler import SAMPLERS, get_sampler

parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str, default="import", choices=["import", "export"])
parser.add_argument("--criterion", type=str, default="entropy", choices=list(SAMPLERS.keys()))
parser.add_argument("--num_samples", type=int, default=10)
parser.add_argument("--project_title", type=str, default="Crypto Sentiment project")
parser.add_argument("--api_key", type=str, required=True)
parser.add_argument("--label_studio_url", type=str, required=True)

if __name__ == "__main__":
    args = parser.parse_args()

    label_studio = LabelStudioProject(
        api_key=args.api_key, label_studio_url=args.label_studio_url, project_title=args.project_title
    )

    sampler = get_sampler(args.criterion, num_samples=args.num_samples)

    if args.mode == "import":
        data = read_data_from_db()

        data_to_import = sampler.get_samples(data)

        label_studio.import_tasks(data_to_import)

    elif args.mode == "export":
        tasks: pd.DataFrame = label_studio.export_tasks(export_type="JSON_MIN")

        if len(tasks) != 0:
            write_data_to_db(tasks, "labeled_news_titles")
