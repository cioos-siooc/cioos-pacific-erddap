# Bucket-migration helpers

One-off tools written on dev-data (vm22) in October 2026, while moving the ERDDAPs onto files restored from
cioos-pacific-bucket. They were left uncommitted on that host; they're kept here so they aren't lost. None of them
runs as part of a deployment.

| Script | Does |
|---|---|
| `fix_file_dirs.py` | rewrites `<fileDir>` in every `datasets.d/*.xml` to the flat `/datasets/<datasetID>/` layout `erddap-sync` restores |
| `merge_regenerated.py` | copies regenerated `datasets.d.restored/*.xml` into `datasets.d/`, skipping datasets already replaced by hand-verified fragments |
| `dump_cdf_metadata.py` | reads a classic NetCDF header directly and prints ERDDAP `/info/<id>/index.json`-shaped metadata (what `erddap-sync` needs to generate a config) |
| `read_cdf_header.py` | lists a classic NetCDF file's dimensions and variables, to check whether a file has data variables at all |
