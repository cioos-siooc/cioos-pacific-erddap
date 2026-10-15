"""Rewrite <fileDir> in every datasets.d/*.xml to match this host's flat
/datasets/<datasetID>/ layout (erddap-sync always restores one directory
per dataset ID), regardless of whatever nested convention the source
fragment used.
"""
import glob
import re

for path in sorted(glob.glob("datasets.d/*.xml")):
    with open(path) as f:
        content = f.read()

    m = re.search(r'datasetID="([^"]+)"', content)
    if not m:
        print(f"SKIP (no datasetID found): {path}")
        continue
    dataset_id = m.group(1)
    correct_file_dir = f"/datasets/{dataset_id}/"

    m2 = re.search(r"<fileDir>(.*?)</fileDir>", content)
    if not m2:
        print(f"SKIP (no <fileDir> found): {path}")
        continue
    if m2.group(1) == correct_file_dir:
        continue  # already correct

    new_content = re.sub(
        r"<fileDir>.*?</fileDir>",
        f"<fileDir>{correct_file_dir}</fileDir>",
        content,
        count=1,
    )
    with open(path, "w") as f:
        f.write(new_content)
    print(f"fixed: {path}  {m2.group(1)} -> {correct_file_dir}")
