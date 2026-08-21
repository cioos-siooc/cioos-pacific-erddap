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

```bash
cd ../cioos-pacific-bucket && docker compose up -d   # brings up SeaweedFS + the bucket
cd ../cioos-pacific-erddap
cp restore-agent.env.sample restore-agent.env   # fill in S3_* / RESTORE_WEBHOOK_TOKEN —
                                                 # must match ../cioos-pacific-bucket/.env exactly
docker compose -f docker-compose.local.yml up -d erddap-restore-agent
```

Then from `cioos-pacific-bucket`, with a `pacific` instance configured with
`restore_webhook_url: http://erddap-restore-agent:8090` in `config.yaml`:

```bash
# IMPORTANT: --data-dir must be /datasets (how the erddap container itself sees the
# mount), not the restore-agent's own internal /erddapData/datasets path — otherwise
# the generated <fileDir> won't match where ERDDAP actually looks.
docker compose run --rm erddap-sync -c /app/config.yaml restore pacific <dataset_id> --data-dir /datasets
```

### TODO: remote host (production / development)

Not yet implemented. The production and development ERDDAP servers are separate remote
machines, reachable today only via SSH (see the `PROD_SERVER_*` / `DEV_SERVER_*` secrets used
by [update-erddap-production-server.yaml](.github/workflows/update-erddap-production-server.yaml)
and [update-erddap-development-server.yaml](.github/workflows/update-erddap-development-server.yaml)),
so the local setup above — shared Docker network, loopback port — doesn't carry over directly.
Rough plan:

1. **Deploy the agent on the remote host itself**, as a service in `docker-compose.yml` (the
   one actually running on those hosts, not `docker-compose.local.yml`), not sharing a Docker
   network with `cioos-pacific-bucket` (which runs elsewhere). Bind its port to loopback only,
   same as local, and reach it either over an SSH tunnel
   (`ssh -L 8090:localhost:8090 <prod-or-dev-host>`) run from wherever `erddap-sync restore` is
   invoked, or over a private/VPC network restricted by firewall to the bucket host's IP —
   never publish it on a public interface.
2. **Provision real secrets on the remote host** — `RESTORE_WEBHOOK_TOKEN` and the S3
   credentials — as GitHub Actions secrets synced to the host's `restore-agent.env`, the same
   way `PROD_SERVER_SSH_KEY` etc. are already managed. Do not reuse the shared local-dev token
   committed nowhere but also not treated as secret today.
3. **Two separate destinations**: prod and dev are different hosts, so this needs either two
   `erddap_instances` entries in `cioos-pacific-bucket`'s `config.yaml` (`prod`, `dev`), each
   with its own `restore_webhook_url` and tunnel/network path, or a shared bastion pattern that
   both reuse.
4. **Keep restore on-demand, not part of every deploy** — the existing SSH `git pull` +
   `--hardFlag` flow in `update-erddap.sh` stays the routine deploy path; `restore` remains a
   manual disaster-recovery / single-dataset-recovery tool triggered separately, run from
   wherever `cioos-pacific-bucket` is operated.
5. **`datasets.d.restored/` review step changes** — a reviewer needs to pull generated
   fragments off the remote host (e.g. `scp`) before diffing and committing them, since there's
   no shared filesystem like the local sibling-checkout setup has.
6. **Document the new secrets** in `sample.env`/`restore-agent.env.sample` and the deployment
   runbook, alongside the existing `PROD_SERVER_*` / `DEV_SERVER_*` GitHub Actions secrets.