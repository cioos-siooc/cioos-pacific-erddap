#!/usr/bin/env python3
"""Checks on datasets.d/ that a broken deployment would otherwise reveal on a live ERDDAP.

    python3 .github/workflows/check-datasets.py [datasets.d]

- every fragment parses as XML (no leftover merge-conflict markers) and holds exactly one <dataset>
- the file is named after its datasetID, and no datasetID appears twice
- file-based datasets read /datasets/<datasetID>/, the layout cioos-pacific-bucket's `pull` and restore write
  (any other fileDir is empty on a server rebuilt from the bucket)
- database datasets connect through the hakai_database_connection placeholder, never a literal JDBC URL with
  credentials (init.d/replace-datasets-secrets.sh fills it in from .env)
Exits 1 and lists every problem.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FILE_TYPES_WITHOUT_FILEDIR = {"EDDTableFromDatabase", "EDDTableFromErddap", "EDDGridFromErddap",
                              "EDDTableFromDapSequence", "EDDGridFromDap", "EDDTableFromHyraxFiles"}
SECRET_PLACEHOLDER = "hakai_database_connection"


def check(directory: Path) -> list[str]:
    problems, seen = [], {}
    files = sorted(directory.glob("*.xml"))
    if not files:
        return [f"no dataset fragments in {directory}"]
    for path in files:
        text = path.read_text(encoding="utf-8")
        if any(m in text for m in ("<<<<<<<", "\n=======\n", ">>>>>>>")):
            problems.append(f"{path.name}: merge-conflict markers")
            continue
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            problems.append(f"{path.name}: not valid XML ({e})")
            continue
        datasets = [root] if root.tag == "dataset" else root.findall("dataset")
        if len(datasets) != 1:
            problems.append(f"{path.name}: {len(datasets)} <dataset> elements, expected 1")
            continue
        ds = datasets[0]
        dataset_id, kind = ds.get("datasetID", ""), ds.get("type", "")
        if path.stem != dataset_id:
            problems.append(f"{path.name}: datasetID is {dataset_id!r}")
        if dataset_id in seen:
            problems.append(f"{path.name}: datasetID {dataset_id!r} also in {seen[dataset_id]}")
        seen[dataset_id] = path.name
        file_dir = ds.findtext("fileDir")
        if kind == "EDDTableFromDatabase":
            source = (ds.findtext("sourceUrl") or "").strip()
            if source != SECRET_PLACEHOLDER:
                problems.append(f"{path.name}: sourceUrl should be the {SECRET_PLACEHOLDER} placeholder "
                                "(a literal URL would publish its credentials; not printed here)")
        elif kind not in FILE_TYPES_WITHOUT_FILEDIR:
            expected = f"/datasets/{dataset_id}/"
            if file_dir is None:
                problems.append(f"{path.name}: {kind} without <fileDir>")
            elif file_dir.strip() != expected:
                problems.append(f"{path.name}: fileDir {file_dir.strip()!r}, expected {expected!r} (bucket layout)")
    return problems


if __name__ == "__main__":
    directory = Path(sys.argv[1] if len(sys.argv) > 1 else "datasets.d")
    problems = check(directory)
    for p in problems:
        print(f"ERROR {p}", file=sys.stderr)
    print(f"{len(list(directory.glob('*.xml')))} fragments checked, {len(problems)} problem(s)")
    sys.exit(1 if problems else 0)
