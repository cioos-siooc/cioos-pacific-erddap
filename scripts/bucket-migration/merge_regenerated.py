"""Copy freshly-regenerated datasets.d.restored/*.xml (from a full
`erddap-sync restore pacific`, using today's fully-fixed engine.py) into the
live datasets.d/, but skip any dataset ID we've already replaced with a
hand-verified known-good fragment pulled from pac-dev2's production ERDDAP
(those cover cases auto-generation can't handle, e.g. BCSOP_daily/
BCSOP_monthly needing EDDTableFromMultidimNcFiles instead of
EDDTableFromNcFiles).
"""
import glob
import os

KEEP_PACDEV2_VERSION = {
    "BCSOP_daily", "BCSOP_monthly",
    "IOS_BOT_Profiles", "IOS_CTD_Moorings",
    "IOS_CTD_Profiles", "IYS_2019_CTD", "IYS_2019_POM",
    "IYS_2019_nutrients_O2", "IYS_2020_CTD", "IYS_2022_TINRO_CTD",
    "IYS_NISKIN_chl_phaeo", "PRIMED_wavebuoy", "IOS_P26_Annualized",
    # DFO_MEDS_BUOYS_HISTORIC, IOS_ADCP_Moorings, IOS_CUR_Moorings removed
    # earlier: pac-dev2's fileNameRegex is tailored to their own naming
    # convention (e.g. ".*\.adcp\.L1\.nc") which doesn't match this host's
    # actual restored filenames (erddap-sync's own <id>_<year>.nc
    # convention), causing "0 files found" even though the data is present
    # and correct. The auto-generated fragment uses the generic ".*\.nc"
    # regex instead.
    #
    # dfo_pbs_nearshore_sensor_data, jklymak_mvp, MPA_SST_timeseries,
    # IOS_DRF, IOS_TOB, IOS_UBC_profiles removed: these had no backed-up
    # .nc data on this host when the pac-dev2 fragments were first merged
    # in (their fileDir pointed at empty directories), but have since been
    # freshly backed up from dev2.cioos.org via `erddap-sync backup-dataset`
    # -- the auto-generated fragment now has real data to point at.
    #
    # NEP36_CanOE, gov.noaa.nodc_0144340 still have no backed-up data at
    # all (NEP36_CanOE is griddap and too large for erddap-sync's current
    # tabledap-only chunked-timeout retry; gov.noaa.nodc_0144340 is a raw
    # CSV/FTP-mirror dataset outside erddap-sync's .nc-file model) --
    # doesn't matter whether kept or not since datasets.d.restored/ has no
    # fragment for them either way.
}

copied = 0
skipped_kept = 0
for path in sorted(glob.glob("datasets.d.restored/*.xml")):
    dataset_id = os.path.splitext(os.path.basename(path))[0]
    if dataset_id in KEEP_PACDEV2_VERSION:
        skipped_kept += 1
        continue
    dst = os.path.join("datasets.d", os.path.basename(path))
    with open(path) as f:
        content = f.read()
    with open(dst, "w") as f:
        f.write(content)
    copied += 1

print(f"copied {copied} regenerated fragments into datasets.d/")
print(f"kept pac-dev2 version for {skipped_kept} datasets (not overwritten)")
