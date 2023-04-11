#!/bin/bash
[ -f ./.env ] && source ./.env
docker run --rm -it \
  -v "${ERDDAP_DATASETS_DIR:-$(pwd)/datasets}:/datasets" \
  -v "$(pwd)/erddap/data/logs:/erddapData/logs" \
  ${ERDDAP_CONTAINAR_NAME:-axiom/docker-erddap:latest} \
  bash -c "cd webapps/erddap/WEB-INF/ && bash GenerateDatasetsXml.sh -verbose"