# CIOOS Pacific ERDDAP Config

This repo stores CIOOS Pacific ERDDAP datasets `datasets.d/*.xml` which is used by CIOOS Pacific's ERDDAP at <https://data.cioospacific.ca/erddap/> and the dev site at <https://pac-dev2.cioos.org/erddap/>. It also provides a `docker-compose.local.yaml` file so you can test out your changes on your local machine.

| Server | Linter | Server Update |
| --- | --- |--- |
| https://data.cioospacific.ca/erddap | ![Lint Code Base](https://github.com/cioos-siooc/cioos-pacific-erddap/actions/workflows/review-datasets-xml.yaml/badge.svg) |![Production Server](https://github.com/cioos-siooc/cioos-pacific-erddap/actions/workflows/update-erddap-servers.yaml/badge.svg?branch=main)|
| https://pac-dev2.cioos.org/erddap | ![Lint Code Base](https://github.com/cioos-siooc/cioos-pacific-erddap/actions/workflows/review-datasets-xml.yaml/badge.svg?branch=development) | ![Development Server](https://github.com/cioos-siooc/cioos-pacific-erddap/actions/workflows/update-erddap-servers.yaml/badge.svg?branch=development)|


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
