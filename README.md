# Cryptonews sentiment barometer application

This is a cryptonews sentiment prediction application [cryptobarometer.org](https://cryptobarometer.org).

<center>
<img src='static/img/react_front_app1.png' width=700>
</center>

Below is an architecture skecth of the application's backend.

<center>
<img src='static/img/demo_cryptosentiment_arch_sketch_v1.png' width=700>
</center>

The general idea of the workflow is the following (__bolded__ verbs below correspond to arrows in the diagram above):

- `Database` (PostgreSQL) stores 3 tables: one for raw news titles (title\_id, title, source, timestamps), one more for model predictions (title\_id, negative, neutral, positive, predicted_class, entropy), and a third one for labeled news titles (title\_id, label, timestamps)
- `Crawler` periodically __scrapes__ news from RSS feeds, filters them, and __writes__ this data to the `Database`;
- `ML model API` service hosts the ML model inference API (model training is not covered here);
- the `Model Scorer` service periodically __reads__ those news titles from the `Database` that lack model predictions, __invokes__ `ML model API` for these fresh titles and __writes__ the result to the `Database`;
- `Data Provider` service __reads__ news titles from the `Database` with its model predictions and provides it to `Frontend` via API;
- `Frontend` __reads__ a metric (average sentiment score for all news titles for the last 24 hours) from the `Data Provider` and visualizes it as a barometer. It also gets a list of latest news from the `Data Provider` as well as historical news sentiment values and depicts them;
- `Scheduler` launches `Crawler`, `Model Scorer`, and `LabelStudio` on a schedule, e.g. 4 times a day;
- `MLflow` allows to track ML experiments and provides model registry interface with models being stored in `Minio`;
- `Label Studio` __reads__ unlabeled data from the `Database` based of an active learning criterion (e.g. entropy) stored in the `model_predictions` table and imports this data into the Label Studio project. Annotator `annotate` the tasks, and then  `Label Studio` __writes__  labeled data to the `Database`, `labeled_news_titles` table.

## Running the app

All components except for the database are packed together and managed by `docker-compose`. See [`docker-compose.yml`](docker-compose.yml) which lists all services and associated commands. At the moment, the database is spun up separately, manually.

**Preparation:**

 - install [`docker`](https://docs.docker.com/engine/install/ubuntu/) and [`docker-compose`](https://docs.docker.com/compose/install/). Tested with Docker version 20.10.14 and docker-compose v2.4.1 (make sure it's docker-compose v2 not v1, we had to add the path to docker-compose to the PATH env variable: `export PATH=/usr/libexec/docker/cli-plugins/:$PATH`);
 - put variables from [this Notion page](https://www.notion.so/d8eaed6d640640e59704771f6b12b603) (section "Project env variables", limited to project contributors) in the `.env` file, see `.env.example`
 - check `volumes/pgadmin` and `volumes/postgres` permissions, if they are root-only, run `sudo chown -R <username> <folder_name>; sudo chmod -R 777 <folder_name>`for both folders (otherwise, they won't be accessible inside docker);
 - if you have trained a model with [`train`](#to-train-the-model) service before, you need to specify model name and model version in configs. Otherwise either run [`train`](#to-train-the-model) service first or put the model file into `static/models`, at the moment the model file `/artifacts/models.logit_tfidf_btc_sentiment.onnx` is stored on the Hostkey machine (limited to project contributors) ;

**To launch the whole application:**

```
docker compose -f docker-compose.yml --profile production up --build
```

This will open a React app `http://<hostname>:3000` in your browser, see a screenshot below in the [Frontend](#frontend) section.

**To set up labeling with LabelStudio:**

There's one non-automated step: to label data, one needs a LabelStudio access token. This token can not be read with LabelStudio API but rather needs to be communicated to the app manually. To provide this token:

- go to LabelStudio (https//:\<server-ip\>:8080);
- create an account (in needs to be created from scratch each time `docker-compose` is relaunched);
- go to Accounts & Settings (upper-right corner in the LabelStudio interface) and copy the access token;
- put the access token into the `.env` file as LABEL\_STUDIO\_ACCESS\_TOKEN.

For more details, see the [Label Studio](#label-studio) section.

### **To train the model:**

 - select model config in the conf/config.yaml file. Available configs can be found in the conf/models folder.
 - place data in the data folder. Specify the path to the data in the config (path_to_data key). This will be replaced with reading from a database.
 - make sure that other services are stopped: `docker compose stop` and `docker compose rm`.
 - run the following command

```
USER=$(id -u) GROUP=$(id -g) docker compose -f docker-compose.yml --profile train up --build
```

The model checkpoint will be saved with the path specified with `checkpoint_path` key in the model config. Onnx model will be saved in `Minio` service and all metrics will be logged to `MLflow`, and another copy of onnx model will be saved locally with the path specified with `path_to_model` key in the model config. If you would like to train a model while other services are running add `-d` option to the command shown above.

**Using gpu to train a model:**

 - enable gpu access with compose: `https://docs.docker.com/compose/gpu-support/`
 - set device: CUDA in model's config
 - run the following command

```
USER=$(id -u) GROUP=$(id -g) docker compose -f docker-compose.yml -f docker-compose.gpu.yml --profile train up --build
```


## Components of the architecture

The app includes the following components:

| **Component**          | **Source**                                                                                         | **Docker-compose service ([`docker-compose.yml`](docker-compose.yml))** |
|------------------------|----------------------------------------------------------------------------------------------------|:--------------------------:|
| PostgreSQL database    | ---                                                                                                |            `db`            |
| PGAdmin                | ---                                                                                                |          `pgadmin`         |
| Crawler                | [`crypto_sentiment_demo_app/crawler/`](crypto_sentiment_demo_app/crawler/)                         |          `crawler`         |
| Model API endpoint     | [`crypto_sentiment_demo_app/model_inference_api/`](crypto_sentiment_demo_app/model_inference_api/) |    `model_inference_api`   |
| Model scoring the news | [`crypto_sentiment_demo_app/model_scorer/`](crypto_sentiment_demo_app/model_scorer/)               |       `model_scorer`       |
| Data provider          | [`crypto_sentiment_demo_app/data_provider/`](crypto_sentiment_demo_app/data_provider/)             |       `data_provider`      |
| Frontend               | [`crypto_sentiment_demo_app/frontend/`](crypto_sentiment_demo_app/frontend/)                       |         `frontend`         |
| Scheduler              | ---                                                                                                |         `scheduler`        |
| Label studio           | [`crypto_sentiment_demo_app/label_studio/`](crypto_sentiment_demo_app/label_studio/)               |       `label_studio`       |
| ML Flow                | ---                                                                                                |          `mlflow`          |
| Model trainer          | [`crypto_sentiment_demo_app/train/`](crypto_sentiment_demo_app/train/)                             |           `train`          |


Below, we go through each one individually.

### Database

Source: `db` service defined in [`docker-compose.yml`](docker-compose.yml)

A PostgreSQL database is set up as a `db` service, see `docker-compose.yml` with initialization scripts provided in the `db_setup` folder. (Previously, it was also configured without Docker on the machine provided by Hostkey see [this](https://www.notion.so/d8eaed6d640640e59704771f6b12b603) Notion page, limited to project contributors).

At the moment, there're 3 tables in the `cryptotitles_db` database:

 - `news_titles` – for raw news: `(title_id BIGINT PRIMARY KEY, title VARCHAR(511) NOT NULL, source VARCHAR(72), pub_time TIMESTAMP))`;
 - `model_prediction` – for model scores produced for each news title: `(title_id BIGINT PRIMARY KEY, negative FLOAT, neutral FLOAT, positive FLOAT, predicted_class INTEGER, entropy FLOAT)`;
 - `labeled_news_titles` – for labeled news: `(title_id BIGINT PRIMARY KEY, label FLOAT, pub_time TIMESTAMP))`.


To run Postgres interactive terminal: `psql -U mlooops -d cryptotitles_db -W` (the password is also mentioned on [this](https://www.notion.so/d8eaed6d640640e59704771f6b12b603) Notion page).

Some commands are:

- `\dt` to list tables
- `select * from news_titles`
- `select count(*) from model_predictions`
- etc. see psql shortcuts [here](https://www.geeksforgeeks.org/postgresql-psql-commands/).

The data can be injested from CSV files into Postgres tables with a custom script [`crypto_sentiment_demo_app/database/write_df_to_db.sh`](crypto_sentiment_demo_app/database/write_df_to_db.sh). In particular, ~4750 labeled titles are populated this way into tables `news_titles` and `labeled_news_titles`:

- `sh crypto_sentiment_demo_app/database/write_df_to_db.sh -p data/20220606_news_titles_to_import.csv -t news_titles`
- `sh crypto_sentiment_demo_app/database/write_df_to_db.sh -p data/20220606_labeled_news_titles_to_import.csv -t labeled_news_titles`

Where files `data/20220606_*_news_titles_to_import.csv` are produced [here](https://github.com/crypto-sentiment/crypto_sentiment_notebooks/pull/13) – those are basically all the labeled data we have, with the only fields left that are matching those in the database.

### Pgadmin

Source: `pgadmin` service defined in [`docker-compose.yml`](docker-compose.yml)

Once the app is running (`docker compose -f docker-compose.yml --profile production up --build`), visit [http://\<IP_ADDRESS\>:8050/browser/]() to launch PGAdmin which is the administration and development platform for PostgreSQL.

<center>
<img src='static/img/pgadmin_interface.png' width=500>
</center>

### Crawler

Source: [`crypto_sentiment_demo_app/crawler/`](crypto_sentiment_demo_app/crawler/)

Crawler reads ~100 RSS feeds defined in `data/crypto_rss_feeds.txt`, and further filters out non-English text, news without a verb, questions and short news (refer to the analysis performed [here](https://github.com/crypto-sentiment/crypto_sentiment_notebooks/tree/main/notebooks/20220530_get_rss_feed_news_perform_eda.ipynb)).

Then it puts the data (title IDs, titles, source, publication timestamps) into the `news_titles` table, and puts titles IDs into the `model_predictions` table to be later picked up by the `model_scorer` service.

### Model inference API

Source: [`crypto_sentiment_demo_app/model_inference_api/`](crypto_sentiment_demo_app/model_inference_api/)

At the moment, we are running a FastAPI with tf-idf & logreg model based on [this repo](https://github.com/crypto-sentiment/crypto_sentiment_model_fast_api). Model training is not covered here, hence the model file needs to be put into the `static/model` folder prior to spinning up the API or be stored in `Minio` and have been logged previosly into `MLflow`.

To be superseded by a more advanced BERT model ([Notion ticket](https://www.notion.so/a74951e4e815480584dea7d61ddce6cc?v=dbfdb1207d0e451b827d3c5041ed0cfd&p=6d47b3b821524a419653151a07cb0ded)).

### Model scorer

Source: [`crypto_sentiment_demo_app/model_scorer/`](crypto_sentiment_demo_app/model_scorer/)

The model scorer service takes those title IDs from the `model_predictions` table that don't yet have predictions (score for `negative`, score for `neutral`, score for `positive`, and `predicted_class`) and calls the Model inference API to run the model against the corresponding titles. It then updates records in the `model_predictions` table to write model predictions into it.

### Data Provider

Source: [`crypto_sentiment_demo_app/data_provider/`](crypto_sentiment_demo_app/data_provider/)

FastAPI service which aggregates the necessary data for our frontend from the database. Run it and check its [`documentation`](http://localhost:8002/docs) for endpoints description and examples.

### Frontend

Source: [`crypto_sentiment_demo_app/frontend/`](crypto_sentiment_demo_app/frontend/)

Curently, the React app looks like this:

<center>
<img src='static/img/react_front_app1.png' width=500>
<img src='static/img/react_front_app2.png' width=500>
</center>


The frontend itself talks to the database to get the average `positive` score for today's news titles (this will be changed in the future, TODO: describe how Frontend talks to the data provider service to get metrics to visualize.).


### Scheduler

Source: `scheduler` service defined in [`docker-compose.yml`](docker-compose.yml)

We use [Ofelia](https://github.com/mcuadros/ofelia) job scheduler that is specifically designed for Docker environments and is easy to use with docker-compose.

The scheduler manages `crawler` and `model_scorer`.

To see it in action:

- launch the app: `docker compose -f docker-compose.yml --profile production up --build`
- check scheduler logs: `docker-compose logs scheduler`
- additionally, you can check the number of records in the `news_titles` and `model_predictions` tables (they will be growing in time). For that, launch [PGAdmin](), navigate to Servers -> <SERVER_NAME> (e.g. "Docker Compose") -> Databases -> <DB_NAME> (e.g. "cryptotitles_db"), then select Tools -> Query Tool and type your SQL: `select count(*) from news_titles`.

### MLflow

You can check your ML experiments and models by visiting http://<server-ip>:8500/.

### Label Studio

Source: [`crypto_sentiment_demo_app/label_studio/`](crypto_sentiment_demo_app/label_studio/)

Label Studio service allows us to annotate additional data.

To launch the service:

- run the app: `docker compose -f docker-compose.yml --profile production up --build`
- This will launch Label Studio at http://\<server-ip\>:8080/


Further, the scheduler picks it up, creates a LabelStudio project and performs imports of data into and exports on schedule. See the "label_studio" service definition in the [`docker-compose.yml`](docker-compose.yml) file.


#### Importing/exporting data

It's also possible to import unlabeled data into LabelStudio and to export labeled data from LabelStudio manually. For that, you need to log into the running container with Label Studio: `docker ps` show running containers, there you can copy the Label Studio container ID and run `docker exec -it \<container_id\> /bin/bash`.

**Importing data into Label Studio**

From inside the running container,

```
bash /home/crypto_sentiment_demo_app/crypto_sentiment_demo_app/label_studio/modify_tasks.sh \
-p <project name> \
-m import \
-c <active learning sampling strategy> \
-n <number of items to sample>
```

creates a new Label Studio project, loads samples from the `model_predictions` table and also creates annotation tasks. Visit http://\<server-ip\>:8080/ to find your new project there.

Two sampling strategies are available: `least_confidence` and `entropy`. Also, the `model_predictions` table will be modified so that `is_annotation` flag will be set to `True` for the imported samples.

**Exporting data from Label Studio**


From inside the running container,

```
bash /home/crypto_sentiment_demo_app/crypto_sentiment_demo_app/label_studio/modify_tasks.sh \
 -p <project_name> \
 -m export
```

exports the annotated and submitted tasks from the Label Studio project and writes them to the `labeled_news_titles` table.

### Github runner (dev)

To add self-hosted Github runner:

- Navigate to the main page of the repository
- **Settings** -> **Actions** -> **Runners**
- Click **New self-hosted runner** and follow the instructions to download and configure the GitHub Actions Runner

We are using setup-python action to setup a python environment. The following steps required for this action to work with a self-hosted runner:

- Put the variable `AGENT_TOOLSDIRECTORY=/opt/hostedtoolcache` into the `.env` file.
- Create a directory called `hostedtoolcache` inside `/opt`
- Run: `sudo chown <user name>:<user group> /opt/hostedtoolcache/`

To launch the runner:

- `cd actions-runner`
- `sudo ./svc.sh install root`
- `sudo ./svc.sh start`

To stop the runner:
`sudo ./svc.sh stop`

## Acknowledgements

We are very grateful to [Hostkey](https://www.hostkey.ru/) and [dstack.ai](https://dstack.ai/) for providing computational resources, both GPU and CPU, for the project.
