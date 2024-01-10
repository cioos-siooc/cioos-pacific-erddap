#!/bin/bash
[ -f .env ] && export $(grep -v '^#' .env | xargs)
docker exec -it "${CONTAINER_NAME:-erddap}" bash -c "cd webapps/erddap/WEB-INF/ && bash DasDds.sh $*" \
  