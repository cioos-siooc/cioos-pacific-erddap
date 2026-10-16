#!/usr/bin/env bash
# Pull the datasets cioos-pacific-pipeline writes straight into cioos-pacific-bucket (BC Lightstations from DFO's
# quarterly releases; DFO PBS nearshore sensors from DFO's GitLab repository) and have ERDDAP reload them. For a host that serves the bucket's files (README: "Remote host:
# rebuild from the bucket" and "Datasets a pipeline updates"): dev-data and stage now, prod once it's rebuilt.
#
#   ./pull-managed-datasets.sh                       # BCSOP_daily, BCSOP_monthly, dfo_pbs_nearshore_sensor_data
#   MANAGED_DATASETS="BCSOP_daily" ./pull-managed-datasets.sh
#
# cron, weekly after the pipeline's Monday 06:00 UTC check:
#   30 7 * * 1  cd /opt/cioos-pacific-erddap && ./pull-managed-datasets.sh >> pull-managed-datasets.log 2>&1
set -euo pipefail
cd "$(dirname "$0")"

read -r -a datasets <<< "${MANAGED_DATASETS:-BCSOP_daily BCSOP_monthly dfo_pbs_nearshore_sensor_data}"
echo "$(date -u +%FT%TZ) pulling ${datasets[*]}"
docker compose -f docker-compose.restore.yml run --rm bucket-pull \
  pull --data-dir /datasets --flag-dir /hardFlag "${datasets[@]}"
