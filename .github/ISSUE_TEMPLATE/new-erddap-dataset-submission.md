---
name: New ERDDAP Dataset Submission
about: To Do list associated to a new CIOOS Pacific ERDDAP dataset submission.
title: 'New ERDDAP Dataset: datasetID'
labels: 'new submission'
assignees: ''

---

## CIOOS Pacific Dataset Submission
This github issue present the different steps associated with the creation of a CIOOS Pacific ERDDAP dataset.

*Related links:*
- [ ] Development ERDDAP Dataset: https://pac-dev2.cioospacific.ca/erddap/...
- [ ] CIOOS Pacific Metadata Form:
- [ ] CIOOS Pacific Catalogue:
- [ ] Production ERDDAP Dataset: https://data.cioospacific.ca/erddap/...
--------

## Submission steps
### Initial Submission
- [ ] Original Data Source is available
- [ ] CIOOS Metadata Form is completed

### ERDDAP Dataset Creation (Data Integrator)
- [ ] Dataset Transformation
- [ ] Near Real-time Data Integration
- [ ] QARTOD Integration
- [ ] ERDDAP Integration
- [ ] ERDDAP Dataset Documentation
- [ ] ERDDAP tested locally
- [ ] Add Dataset to Development Branch
- [ ] ERDDAP Global Attributes are matching the Metadata Record associated fields (see Metadata Form ERDDAP Snippet)

### Related Issues
List any issues related to this dataset submission that need to be reviewed prior to the submission.
- [ ] ...

### Dataset Approuval
The dataset provider needs to approve the dataset present within the CIOOS Pacific ERDDAP development server prior to make it available in production.
- [ ] Development Dataset approved

-----
### Dataset Deployment in Production
This section list the differents steps needed to make an ERDDPAP dataset available in production.

#### ERDDAP
- [ ] Merge Development  ERDDAP Dataset to Production Branch
- [ ] Confirm ERDDAP Dataset is running on [CIOOS Pacific Production ERDDAP Server](https://data.cioospacific.ca/erddap/index.html)
#### Metadata Record
- [ ] Confirm Metadata Record is pointing to the Production ERDDAP dataset
- [ ] Publish Metadata record
- [ ] Confirm Metadata record is available appropriately on the [CIOOS Pacific](https://catalogue.cioospacific.ca/dataset)
- [ ] Confirm Metadata record is available appropriately on the [CIOOS National](https://catalogue.cioos.ca/dataset)

### DOI
- [ ] Generate DOI associated with CIOOS Pacific CKAN dataset page?
- [ ] COMPLETED
