# CIOOS Pacific ERDDAP Config

This repo stores CIOOS Pacific ERDDAP datasets `datasets.d/*.xml` which is used by CIOOS Pacific's ERDDAP at <https://data.cioospacific.ca/erddap/> and the dev site at <https://pac-dev2.cioos.org/erddap/>. It also provides a `docker-compose.local.yaml` file so you can test out your changes on your local machine.

| Server | Linter | Server Update |
| --- | --- |--- |
| https://data.cioospacific.ca/erddap | ![Lint Code Base](https://github.com/cioos-siooc/cioos-pacific-erddap/actions/workflows/review-datasets-xml.yaml/badge.svg) | [![Update Main ERDDAP server](https://github.com/cioos-siooc/cioos-pacific-erddap/actions/workflows/update-erddap-production-server.yaml/badge.svg?branch=main)](https://github.com/cioos-siooc/cioos-pacific-erddap/actions/workflows/update-erddap-production-server.yaml)|
| https://pac-dev2.cioos.org/erddap | ![Lint Code Base](https://github.com/cioos-siooc/cioos-pacific-erddap/actions/workflows/review-datasets-xml.yaml/badge.svg?branch=development) | [![Update Development ERDDAP server](https://github.com/cioos-siooc/cioos-pacific-erddap/actions/workflows/update-erddap-development-server.yaml/badge.svg?branch=development)](https://github.com/cioos-siooc/cioos-pacific-erddap/actions/workflows/update-erddap-development-server.yaml)|


## Creating .xml snippet files for your dataset
This repository relies on the `docker-erddap` docker container and uses the experimental `datasets.d` feature available within this container (see more documentation [here](https://github.com/axiom-data-science/docker-erddap)). To include a new dataset, apply the following steps:
- create one .xml file in `datasets.d` for each dataset. Use `GenerateDatasetsXml.sh` to generate a new dataset xml.
- the filename should match the dataset ID _exactly_ (best to copy and paste)
- the file should start with `<dataset>` and end with `</dataset>`. There should be no XML prolog (
  remove `<?xml...`)
- if you have a `fileDir` line, the folder name should also match your dataset ID _exactly_ : `<fileDir>/datasets/<your_dataset_id></fileDir>`

## Compliance checker
A compliance check is completed nightly on a subset of every datasets by the CIOOS [`erddap-compliance-runner`](https://github.com/cioos-siooc/erddap-compliance-runner) using the IOOS Compliance Checker tool. A link to the results is added to each erddap datasets in the upper right corner.

We are testing compliance for the CF1.6, ACDD 1.3 standards.

## Configuration 
The different components of the ERDDAP system and datasets configuration are defined through the environment variables present within the docker container. 
To start a new configuration create a copy of the `sample.env` file as `.env` and fill up the different items available. The environment variables are following three main categories:
- ERDDAP_.* variables are used to overwrite any components available within the erddap `setup.xml`. 
- ERDDAP_DATASET_(.*) variables are used to define top level elements of the dataset.xml, see [ERDDAP Docs](https://coastwatch.pfeg.noaa.gov/erddap/download/setupDatasetsXml.html#details) for full list of parametesr. This component is using the EXPERIMENTAL feature `/datasets.d.sh` of [docker-erddap](https://github.com/axiom-data-science/docker-erddap).
- ERDDAP_SECRET_(.*) is used to replace any expressions present within the datasets.xml by a certain value. This can be use to keep certain information secret. This component is using the EXPERIMENTAL feature `/init.d/*` of [docker-erddap](https://github.com/axiom-data-science/docker-erddap) and is handled by [init.d/replace-datasets-secrets.sh](init.d/replace-datasets-secrets.sh)

## Setup

### Testing environment
- Install [docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/)
- put your data files (eg .nc files) into the datasets folder
- edit the config files in the config directory. After editing them you will need to run `sh update-erddap.sh` to create datasets.xml
- Run `docker-compose up`. On unix systems you will need to run with `sudo`
- See if it works by going to <http://localhost:8090/erddap>

### Production and Development environments
For both servers, configuration is handled within the `.env` file which  overwrites fields present within the `setup.xml` through the `ERDDAP_*` variables, expressions to hidden within the datasets.xml are defined by the variables `ERDDAP_SECRET_*`. Pushes to main and development branches triggers an update of each associated servers via the update [workflow](.github/workflows/update-erddap-servers.yaml)
- [CIOOS Pacific Production ERDDAP](https://data.cioospacific.ca/erddap/) (branch = main)
- [CIOOS Pacific Development ERDDAP](https://pac-dev2.cioospacific.ca/erddap/) (branch = development)

## Use ERDDAP docker container
The following commands are usefull for handling an erdddap docker container:
- Start container: `docker-compose up -d`
- Restart container: `docker restart erddap` or `docker-compose restart`
- Stop container: `docker-compose down`

## Troubleshooting
- See ERDDAP Status page <http://localhost:8090/erddap/status.html>
- See ERDDAP log `erddap/data/logs/log.txt` for more information
- Test your dataset with the following command: `sh DasDds.sh` And then type in a dataset ID

## Restoring from cioos-pacific-bucket

[cioos-pacific-bucket](https://github.com/cioos-siooc/cioos-pacific-bucket) backs up ERDDAP
datasets to a SeaweedFS (S3-compatible) bucket and can push them back to an ERDDAP host
on demand via its `restore` command — useful for recovering a dataset, or repopulating this
repo's `datasets/` folder after a rebuild, without waiting on the passive cron/git flow.

### Local host (implemented)

`docker-compose.local.yml` runs an `erddap-restore-agent` service — the destination side of
`cioos-pacific-bucket`'s restore command — for when both repos are checked out as sibling
directories on the same machine. It:

- writes restored `.nc` files into `./datasets/<dataset_id>/`, matching this repo's existing
  `fileDir` convention (see any file in `datasets.d/`)
- writes generated dataset XML into `./datasets.d.restored/` (gitignored) — a **staging** area,
  not the live `datasets.d/`. `datasets.d/` is git-tracked and hand-curated, and is deployed via
  the normal git + CI + SSH flow ([update-erddap.sh](update-erddap.sh)), so restore never writes
  into it directly. Review a generated fragment and `git add` it yourself if it looks right.
- touches `./erddap/data/hardFlag/<dataset_id>` per restored dataset, reusing the exact reload
  mechanism `update-erddap.sh --hardFlag` already uses — no new reload path introduced
- is bound to `127.0.0.1:8091` only (never reachable off the host), and joins
  `cioos-pacific-bucket_default` (declared as an `external` network) so it can resolve
  `seaweedfs-s3` by name without any change to that repo's compose file

Setup:

> **Port collision warning:** `cioos-pacific-bucket/docker-compose.yml` ships its own bundled
> `erddap-restore-agent` — a self-contained fake destination it uses to test its own
> backup→restore loop in isolation — published on host port **8090**. That's the same host
> port this repo's real `erddap` container uses (`HOST_PORT:-8090:8080`). On a host running
> both repos side by side, a plain `docker compose up -d` in `cioos-pacific-bucket` will try to
> bind 8090 twice and fail with `port is already allocated`. You don't need that bundled agent
> here at all — the real destination-side agent is the one below, on port 8091. Bring up only
> what the bucket needs instead:
> ```bash
> cd ../cioos-pacific-bucket
> docker compose up -d seaweedfs-master seaweedfs-volume seaweedfs-filer seaweedfs-s3 init-bucket erddap-sync
> ```

```bash
cd ../cioos-pacific-erddap
cp restore-agent.env.sample restore-agent.env   # fill in S3_* / RESTORE_WEBHOOK_TOKEN —
                                                 # must match ../cioos-pacific-bucket/.env exactly
docker compose -f docker-compose.local.yml up -d erddap-restore-agent
```

Then from `cioos-pacific-bucket`, with a `pacific` instance configured with
`restore_webhook_url: http://pacific-erddap-restore-agent:8090` in `config.yaml`. Use that name, not
`erddap-restore-agent`: the bucket stack's own test agent has that name on the same network, so it can
answer instead of this one.

```bash
# IMPORTANT: --data-dir must be /datasets (how the erddap container itself sees the
# mount), not the restore-agent's own internal /erddapData/datasets path — otherwise
# the generated <fileDir> won't match where ERDDAP actually looks.
# erddap-sync is behind the bucket repo's `manual` profile. A restore takes the bucket's write lock (it
# regenerates erddap-config/<id>.xml there), so it waits for a running backup to finish.
docker compose --profile manual run --rm erddap-sync -c /app/config.yaml restore pacific <dataset_id> --data-dir /datasets
```

### Remote host: rebuild from the bucket

A server away from the bucket (the rebuilt data.cioospacific.ca, stg-data.cioospacific.ca) gets its datasets with
`erddap-sync pull` (cioos-pacific-bucket), which only reads the bucket, and serves them with the git-tracked
`datasets.d/`: every `fileDir` is `/datasets/<dataset_id>/`, the layout `pull` writes. No restore-agent, shared
Docker network or SSH tunnel is involved. Tested on oncstage2 (stg-data.cioospacific.ca) on 2026-10-14: all
datasets load and match dev-data.

1. **Checkouts**: this repo, and cioos-pacific-bucket beside it (or set `BUCKET_REPO_DIR` in `.env`).
2. **`.env`** (from `sample.env`), besides the usual ERDDAP settings:
   - `ERDDAP_baseUrl` / `ERDDAP_baseHttpsUrl`: the public URL, e.g. `https://stg-data.cioospacific.ca`
   - `ERDDAP_MAX_MEMORY`: at least `8G` for the full catalogue
   - `COMPOSE_PROFILES=pipelines-db`, `PIPELINES_DB_HOSTNAME`, `ERDDAP_SECRET_hakai_database_connection`: for
     DFO_MEDS_BUOYS and ECCC_MSC_BUOYS (see "Database from cioos-pipelines")
   - `BUCKET_S3_ENDPOINT`: the bucket's S3 gateway as this host reaches it (default `https://s3.cioospacific.ca`;
     on ONC's network `http://142.104.198.53:8333` is direct and much faster)
   - `TOMCAT_USER_ID` / `TOMCAT_GROUP_ID`: the host user that owns `DATASETS_DIR`
3. **`restore-agent.env`** (from `restore-agent.env.sample`): `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`. Keep it
   mode 600; a read-only key is enough.
4. **Pull the datasets** (about 155 GB; `DATASETS_DIR` must be writable by `TOMCAT_USER_ID`):
   ```bash
   docker compose -f docker-compose.restore.yml run --rm --build bucket-pull
   ```
   Rerunning it overwrites what's there. One dataset: append `pull --data-dir /datasets <dataset_id>`.
5. **Start ERDDAP**; with `COMPOSE_PROFILES=pipelines-db` the DB sidecar starts too. The container builds
   `datasets.xml` from `datasets.d/` and fills in the secret on startup:
   ```bash
   docker compose up -d
   ```
   On a fresh start ERDDAP defers every new dataset to the end of the first load, so `status.html` lists them as
   failed until the next major load. Compare the result with the other servers using cioos-pacific-pipeline's
   `scripts/compare-erddaps.py <url> ...`.
6. **Publish it** through a Cloudflare Tunnel: `sudo cloudflared service install <token>`, then install
   [cloudflared/override.conf](cloudflared/override.conf) as
   `/etc/systemd/system/cloudflared.service.d/override.conf`, `sudo systemctl daemon-reload` and
   `sudo systemctl restart cloudflared`. The tunnel's public hostname points at `http://localhost:8090` (path empty);
   a Cloudflare redirect rule sends `/` to `/erddap/index.html`, since Tomcat serves nothing at the root.

### Datasets a pipeline updates

`BCSOP_daily` and `BCSOP_monthly` (BC Lightstations) are written straight into the bucket by cioos-pacific-pipeline's
`bcsop` flow from DFO's releases, about every three months. Their manifests say `managed_by`, so the bucket's
ERDDAP backups never replace them with an ERDDAP's copy. A host gets each new version with
[pull-managed-datasets.sh](pull-managed-datasets.sh), which pulls just those datasets and drops a `hardFlag` so ERDDAP
reloads them, quickRestart or not. Run it weekly from cron after the flow's Monday check:

```bash
30 7 * * 1  cd /opt/cioos-pacific-erddap && ./pull-managed-datasets.sh >> pull-managed-datasets.log 2>&1
```

Same setup as a rebuild (`restore-agent.env`, `BUCKET_S3_ENDPOINT`, `TOMCAT_USER_ID`). It re-downloads about 50 MB
each time, whether or not there was a release. Prod keeps its own 2019 copy until it's rebuilt from the bucket;
add the cron there at the cutover.

## Database from cioos-pipelines

`DFO_MEDS_BUOYS` and `ECCC_MSC_BUOYS` read the placeholder `hakai_database_connection`, which
`init.d/replace-datasets-secrets.sh` replaces with `ERDDAP_SECRET_hakai_database_connection` from `.env`.
To read them from the [cioos-pipelines](https://github.com/cioos-siooc/cioos-pacific-pipeline) database
instead of db.hakai.org, the optional `pipelines-db` service opens a connection through that stack's
Cloudflare Tunnel. On the ERDDAP server's `.env`:

```bash
COMPOSE_PROFILES=pipelines-db
PIPELINES_DB_HOSTNAME=<database hostname of the pipelines tunnel>
PIPELINES_DB_ACCESS_CLIENT_ID=<Cloudflare Access service token id>
PIPELINES_DB_ACCESS_CLIENT_SECRET=<Cloudflare Access service token secret>
ERDDAP_SECRET_hakai_database_connection=jdbc:postgresql://pipelines-db:5432/cioos?user=erddap\&amp;password=<erddap password>
```

- Write `\&amp;`, not `&`, in the JDBC URL. The replacement script is `sed`, where `&` means "the matched
  text", and the result must be valid XML. The script turns `\&amp;` into `&amp;`, which ERDDAP reads as `&`.
- The password must not contain `@`, `&`, `\`, `<` or `>`. Generate it with `openssl rand -hex 24`.
- `erddap` is a read-only role created on the pipelines stack with `scripts/create-readonly-role.sh erddap`.
- The service token must be allowed by a *Service Auth* policy on the database hostname's Cloudflare Access
  application.

Then `docker compose up -d` (starts `pipelines-db`) and restart `erddap` so the new `.env` value is applied.
Check the connection from the ERDDAP container with `docker compose exec erddap bash -c 'cat < /dev/null > /dev/tcp/pipelines-db/5432 && echo ok'`.

## Server-specific settings

Keep each server's settings in its `.env` (ERDDAP reads any `setup.xml` setting from an `ERDDAP_<setting>`
variable), not in edits to tracked files. A modified `docker-compose.yml` or `erddap/content/setup.xml` makes
`git pull` fail, which silently stops the update workflows. For anything `.env` can't express, use
`docker-compose.override.yml`: Docker Compose loads it automatically, and git ignores it.
