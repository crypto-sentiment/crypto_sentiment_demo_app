# Cryptonews sentiment demo app

This is a demo cryptonews sentiment prediction application. Its goal is to create an MVP and also create a prototype for the interaction of all components. The components themselves are mocks at the moment, to be superseded by more advanced ones.

<center>
<img src='static/img/demo_cryptosentiment_arch_sketch.png' width=500>
</center>

The general idea of the workflow is the following (__bolded__ verbs below correspond to arrows in the diagram above):

- `Database` (PostgreSQL) stores 2 tables: one for raw news titles (title\_id, title, source, timestamsp), another one for model predictions (title\_id, negative, neutral, positive, predicted_class);
- `Crawler` periodically __scrapes__ 50 latest news from [https://bitcointicker.co/news/](https://bitcointicker.co/news/) and __writes__ this data to the `Database`;
- `ML model API` service hosts the ML model inference API (model training is not covered here);
- the `Model Scorer` service periodically __reads__ those news titles from the `Database` that lack model predictions, __invokes__ `ML model API` for these fresh titles and __writes__ the result to the `Database`;
- `Data Provider` service __reads__ news titles from the `Database` with its model predictions and provides it to `Frontend` via API;
- `Frontend` __reads__ a metric (average sentiment score for all news titles for the last 24 hours) from the `Data Provider` and visualizes it as a barometer. Also, users __interact__ with `Frontend` by inserting news titles (i.e. free text), for which `Frontend` __invokes__ `ML model API` to show predictions for the corresponding user-input news titles.

## Running the app

### Running the app with docker-compose

All components except for the database are packed together and managed by `docker-compose`. See [`docker-compose.yml`](docker-compose.yml) which lists all services and associated commands. At the moment, the database is spun up separately, manually.

To launch the whole application:

 - install [`docker`](https://docs.docker.com/engine/install/ubuntu/) and [`docker-compose`](https://docs.docker.com/compose/install/). Tested with Docker version 20.10.14 and docker-compose v2.4.1 (make sure it's docker-compose v2 not v1, I had to add the path to docker-compose to the PATH env variable: `export PATH=/usr/libexec/docker/cli-plugins/:$PATH`);
 - add a DB connection string `postgresql://<user>:<pwd>@<host>:<port>/<database>` to the `db_connection.ini` file (for the exact connection string, refer to [this](https://www.notion.so/d8eaed6d640640e59704771f6b12b603) Notion page, limited to project contributors);
 - put the model pickle file into `static/models` (later this will be superseded by MLFlow registry), at the moment the model file `/artifacts/models.logit_tfidf_btc_sentiment.pkl` is stored on the Hostkey machine;
 - run `docker-compose up`.

This will open a streamlit app `http://<hostname>:8501` in your browser, see a screenshot below in the [Frontend](#frontend) section.

### Running the app without docker-compose

To launch the whole application:

 - install all dependencies listed in `crypto_sentiment_demo_app/*/requirements.txt` files;
 - add the root folder to PYTHONPATH: `export PYTHONPATH=<path_to_this_repo>:$PYTHONPATH`
 - add a DB connection string `postgresql://<user>:<pwd>@<host>:<port>/<database>` to the `db_connection.ini` file (for the exact connection string, refer to [this](https://www.notion.so/d8eaed6d640640e59704771f6b12b603) Notion page, limited to project contributors);
 - run crawler: `python3 -m crypto_sentiment_demo_app.crawler.crawler`;
 - put the model pickle file into `static/models` (later this will be superseded by MLFlow registry), at the moment the model file `/artifacts/models.logit_tfidf_btc_sentiment.pkl` is stored on the Hostkey machine;
 - run model inference API: `uvicorn crypto_sentiment_demo_app.model_inference_api.api:app --port 8001 --reload`;
 - run the model scorer script: `python3 -m crypto_sentiment_demo_app.model_scorer.model_scorer`;
 - run data provider: `uvicorn crypto_sentiment_demo_app.data_provider.api:app --port 8002 --reload`;
 - run Streamlit frontend: `streamlit run crypto_sentiment_demo_app/frontend/streamlit_app.py`

This will open a streamlit app `http://localhost:8501` in your browser, see a screenshot below in the [Frontend](#frontend) section.

## Components of the architecture

The app includes prototypes of the following components:

- PostgreSQL database for raw and model-scored news titles;
- primitive crawler: see [`crypto_sentiment_demo_app/crawler/`](crypto_sentiment_demo_app/crawler/);
- model API endpoint: see [`crypto_sentiment_demo_app/model_inference_api/`](crypto_sentiment_demo_app/model_inference_api/);
- model scoring the news: see [`crypto_sentiment_demo_app/model_scorer/`](crypto_sentiment_demo_app/model_scorer/);
- data provider: see [`crypto_sentiment_demo_app/data_provider/`](crypto_sentiment_demo_app/data_provider/);
- primitive front end: see [`crypto_sentiment_demo_app/frontend/`](crypto_sentiment_demo_app/frontend/).

Below, we go through each one individually.

### Database

Currently, a PostgreSQL database is set up on the machine provided by Hostkey (for access, refer to [this](https://www.notion.so/d8eaed6d640640e59704771f6b12b603) Notion page, limited to project contributors).

At the moment, there're two tables in the `cryptotitles_db` database:

 - `news_titles` – for raw news: `(title_id BIGINT PRIMARY KEY, title VARCHAR(511) NOT NULL, source VARCHAR(36), pub_time TIMESTAMP))`;
 - `model_prediction` – for model scores produced for each news title: `(title_id BIGINT PRIMARY KEY, negative FLOAT, neutral FLOAT, positive FLOAT, predicted_class INTEGER)`.

Later, at least one more table will be added – for labeled news titles.

To run Postgres interactive terminal: `psql -U mlooops -d cryptotitles_db -W` (the password is also mentioned on [this](https://www.notion.so/d8eaed6d640640e59704771f6b12b603) Notion page).

Some commands are:

- `\dt` to list tables
- `select * from news_titles`
- `select count(*) from model_predictions`
- etc. see psql shortcuts [here](https://www.geeksforgeeks.org/postgresql-psql-commands/).

### Crawler

Source: [`crypto_sentiment_demo_app/crawler/`](crypto_sentiment_demo_app/crawler/)

The 1st version of the crawler uses BeautifulSoup to parse 50 news at a time from [https://bitcointicker.co/news/](https://bitcointicker.co/news/). It then writes news titles to the `news_titles` table and title IDs – to the `model_prediction` table.

This is to be superseded by a more advanced crawler ([Notion ticket](https://www.notion.so/a74951e4e815480584dea7d61ddce6cc?v=dbfdb1207d0e451b827d3c5041ed0cfd&p=d5d0948bde5f43c7b77c5e9329d52980)).

### Model inference API

Source: [`crypto_sentiment_demo_app/model_inference_api/`](crypto_sentiment_demo_app/model_inference_api/)

At the moment, we are running a FastAPI with tf-idf & logreg model based on [this repo](https://github.com/crypto-sentiment/crypto_sentiment_model_fast_api). Model training is not covered here, hence the model file needs to be put into the `static/model` folder prior to spinning up the API.

To be superseded by a more advanced BERT model ([Notion ticket](https://www.notion.so/a74951e4e815480584dea7d61ddce6cc?v=dbfdb1207d0e451b827d3c5041ed0cfd&p=6d47b3b821524a419653151a07cb0ded)).

### Model scorer

Source: [`crypto_sentiment_demo_app/model_scorer/`](crypto_sentiment_demo_app/model_scorer/)

The model scorer service takes those title IDs from the `model_predictions` table that don't yet have predictions (score for `negative`, score for `neutral`, score for `positive`, and `predicted_class`) and calls the Model inference API to run the model against the corresponding titles. It then updates records in the `model_predictions` table to write model predictions into it.

### Data Provider

Source: [`crypto_sentiment_demo_app/data_provider/`](crypto_sentiment_demo_app/data_provider/)

FastAPI service which aggregates the necessary data for our frontend from the database. Run it and check its [`documentation`](http://localhost:8002/docs) for endpoints description and examples.

### Frontend

Source: [`crypto_sentiment_demo_app/frontend/`](crypto_sentiment_demo_app/frontend/)

Curently, the streamlit app looks like this:


<center>
<img src='static/img/streamlit_demo_app.png' width=500>
</center>

The frontend itself talks to the database to get the average `positive` score for today's news titles (this will be changed in the future).

This is to be superseded by a more advanced React front end service ([Notion ticket](https://www.notion.so/a74951e4e815480584dea7d61ddce6cc?v=dbfdb1207d0e451b827d3c5041ed0cfd&p=31d73280a5d547bdb8852d3d63d73060)).
