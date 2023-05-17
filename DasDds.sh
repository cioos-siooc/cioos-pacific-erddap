#!/bin/bash
[ -f .env ] && export $(xargs < .env)
docker exec -it "${CONTAINER_NAME:-erddap}" bash -c "cd webapps/erddap/WEB-INF/ && bash DasDds.sh $*" \
  