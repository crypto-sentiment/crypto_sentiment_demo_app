CREATE DATABASE cryptotitles_db
    WITH
    OWNER = mlooops
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

CREATE TABLE IF NOT EXISTS public.news_titles
(
    title_id bigint NOT NULL,
    title character varying(511) COLLATE pg_catalog."default" NOT NULL,
    source character varying(72) COLLATE pg_catalog."default",
    pub_time timestamp without time zone,
    CONSTRAINT news_titles_pkey PRIMARY KEY (title_id)
)

CREATE TABLE IF NOT EXISTS public.model_predictions
(
    title_id bigint NOT NULL,
    negative double precision,
    neutral double precision,
    positive double precision,
    predicted_class integer,
    entropy double precision,
    CONSTRAINT model_predictions_pkey PRIMARY KEY (title_id)
)

CREATE TABLE IF NOT EXISTS public.labeled_news_titles
(
    title_id bigint NOT NULL,
    label integer,
    annot_time timestamp without time zone,
    CONSTRAINT labeled_news_titles_pkey PRIMARY KEY (title_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.news_titles
    OWNER to mlooops;

ALTER TABLE IF EXISTS public.model_predictions
    OWNER to mlooops;

ALTER TABLE IF EXISTS public.labeled_news_titles
    OWNER to mlooops;
