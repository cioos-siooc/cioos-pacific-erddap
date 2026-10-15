"""Read a classic-CDF (CDF-1/2) NetCDF file's real header directly (no
netCDF4/scipy dependency) and emit an ERDDAP /info/<id>/index.json-shaped
JSON blob: one "variable" row per data variable (sourceName + dataType) and
one "attribute" row per NC_GLOBAL attribute (name + value), matching the
exact structure erddap_sync.engine._extract_global_attribute and
_extract_data_variables expect.

Written to backfill metadata for datasets whose original backup-time
/info/ capture never happened and whose source is no longer live, so the
real values (recovered directly from the .nc file already on disk) can be
uploaded to metadata/<id>.json once, making erddap-sync's own generator
produce correct output going forward without host-side XML patches.
"""
import json
import struct
import sys


def pad4(n):
    return (4 - (n % 4)) % 4


def read_name(buf, pos):
    (nelems,) = struct.unpack_from(">I", buf, pos)
    pos += 4
    name = buf[pos:pos + nelems].decode("utf-8", errors="replace")
    pos += nelems + pad4(nelems)
    return name, pos


NC_TYPE_SIZES = {1: 1, 2: 1, 3: 2, 4: 4, 5: 4, 6: 8}
NC_TYPE_STRUCT = {1: "b", 3: ">h", 4: ">i", 5: ">f", 6: ">d"}
NC_TYPE_ERDDAP_NAME = {1: "byte", 2: "String", 3: "short", 4: "int", 5: "float", 6: "double"}


def read_attr_value(buf, pos, nc_type, nelems):
    size = NC_TYPE_SIZES[nc_type]
    total = size * nelems
    raw = buf[pos:pos + total]
    pos += total + pad4(total)
    if nc_type == 2:
        value = raw.rstrip(b"\x00").decode("utf-8", errors="replace")
    else:
        fmt = NC_TYPE_STRUCT[nc_type]
        values = [struct.unpack_from(fmt, raw, i * size)[0] for i in range(nelems)]
        value = values[0] if len(values) == 1 else ", ".join(str(v) for v in values)
    return value, pos


def main(path, dataset_id):
    with open(path, "rb") as fh:
        buf = fh.read(2_000_000)

    magic = buf[0:3]
    version = buf[3]
    if magic != b"CDF":
        raise ValueError(f"not a classic NetCDF file (magic={magic!r})")

    pos = 8  # skip magic+version(4) and numrecs(4)

    # dim_list
    tag, nelems = struct.unpack_from(">II", buf, pos)
    pos += 8
    for _ in range(nelems):
        _, pos = read_name(buf, pos)
        pos += 4  # dim length

    rows = []

    # gatt_list (global attributes)
    tag, nelems = struct.unpack_from(">II", buf, pos)
    pos += 8
    for _ in range(nelems):
        name, pos = read_name(buf, pos)
        nc_type, anelems = struct.unpack_from(">II", buf, pos)
        pos += 8
        value, pos = read_attr_value(buf, pos, nc_type, anelems)
        rows.append(["attribute", "NC_GLOBAL", name, NC_TYPE_ERDDAP_NAME[nc_type], value])

    # var_list
    tag, nelems = struct.unpack_from(">II", buf, pos)
    pos += 8
    for _ in range(nelems):
        name, pos = read_name(buf, pos)
        (ndims,) = struct.unpack_from(">I", buf, pos)
        pos += 4
        pos += 4 * ndims
        vtag, vnelems = struct.unpack_from(">II", buf, pos)
        pos += 8
        for _ in range(vnelems):
            _, pos = read_name(buf, pos)
            vnc_type, vanelems = struct.unpack_from(">II", buf, pos)
            pos += 8
            _, pos = read_attr_value(buf, pos, vnc_type, vanelems)
        nc_type, vsize = struct.unpack_from(">II", buf, pos)
        pos += 8
        if version == 1:
            pos += 4
        else:
            pos += 8
        rows.append(["variable", name, "", NC_TYPE_ERDDAP_NAME[nc_type], ""])

    metadata = {
        "table": {
            "columnNames": ["Row Type", "Variable Name", "Attribute Name", "Data Type", "Value"],
            "rows": rows,
        }
    }
    out_path = f"{dataset_id}.metadata.json"
    with open(out_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"wrote {out_path} ({len(rows)} rows)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
