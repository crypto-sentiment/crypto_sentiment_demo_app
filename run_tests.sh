#!/bin/bash

docker compose -f docker-compose.test.yml build --no-cache

docker run -v $PWD:/root image_model_fast_api_test pytest tests/model_inference_api; output_model_inference=$?
docker run -v $PWD:/root image_model_scorer_test pytest tests/model_scorer; output_model_scorer=$?

if [[ $output_model_inference || $output_model_scorer ]]; then
   exit 1
else
   exit 0
fi
