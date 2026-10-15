"""Minimal read-only parser for the classic NetCDF (CDF-1/2) header, just
enough to list dimensions and variables without any dependencies (no
netCDF4/scipy needed). Not a general-purpose reader -- only enough to
diagnose whether a file actually has data variables defined.
"""
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


def skip_attr_values(buf, pos, nc_type, nelems):
    size = NC_TYPE_SIZES.get(nc_type)
    if size is None:
        raise ValueError(f"unknown nc_type {nc_type}")
    total = size * nelems
    pos += total + pad4(total)
    return pos


def main(path):
    with open(path, "rb") as fh:
        buf = fh.read(2_000_000)  # header is always near the start

    magic = buf[0:3]
    version = buf[3]
    if magic != b"CDF":
        print(f"NOT a classic NetCDF file (magic={magic!r})")
        return
    print(f"magic=CDF version={version}")

    pos = 4
    (numrecs,) = struct.unpack_from(">I", buf, pos)
    pos += 4
    print(f"numrecs={numrecs}")

    # dim_list
    tag, nelems = struct.unpack_from(">II", buf, pos)
    pos += 8
    dims = []
    if tag not in (0, 0x0A):
        raise ValueError(f"unexpected dim_list tag {tag}")
    for _ in range(nelems):
        name, pos = read_name(buf, pos)
        (dimlen,) = struct.unpack_from(">I", buf, pos)
        pos += 4
        dims.append((name, dimlen))
    print(f"dimensions ({len(dims)}): {dims}")

    # gatt_list (global attributes)
    tag, nelems = struct.unpack_from(">II", buf, pos)
    pos += 8
    gatts = []
    if tag not in (0, 0x0C):
        raise ValueError(f"unexpected gatt_list tag {tag}")
    for _ in range(nelems):
        name, pos = read_name(buf, pos)
        nc_type, anelems = struct.unpack_from(">II", buf, pos)
        pos += 8
        pos = skip_attr_values(buf, pos, nc_type, anelems)
        gatts.append(name)
    print(f"global attributes ({len(gatts)}): {gatts}")

    # var_list
    tag, nelems = struct.unpack_from(">II", buf, pos)
    pos += 8
    var_names = []
    if tag not in (0, 0x0B):
        raise ValueError(f"unexpected var_list tag {tag}")
    var_info = []
    for _ in range(nelems):
        name, pos = read_name(buf, pos)
        (ndims,) = struct.unpack_from(">I", buf, pos)
        pos += 4
        dimids = struct.unpack_from(f">{ndims}I", buf, pos)
        pos += 4 * ndims
        vtag, vnelems = struct.unpack_from(">II", buf, pos)
        pos += 8
        for _ in range(vnelems):
            aname, pos = read_name(buf, pos)
            nc_type, anelems = struct.unpack_from(">II", buf, pos)
            pos += 8
            pos = skip_attr_values(buf, pos, nc_type, anelems)
        nc_type, vsize = struct.unpack_from(">II", buf, pos)
        pos += 8
        if version == 1:
            (begin,) = struct.unpack_from(">I", buf, pos)
            pos += 4
        else:
            (begin,) = struct.unpack_from(">Q", buf, pos)
            pos += 8
        var_names.append(name)
        var_info.append((name, ndims, dimids, nc_type, vsize, begin))

    print(f"variables ({len(var_names)}): {var_names}")
    print(f"header_end_pos={pos}")
    import os
    actual_size = os.path.getsize(sys.argv[1])
    print(f"actual_file_size={actual_size}")
    print(f"{'name':20s} {'nc_type':8s} {'vsize':10s} {'begin':12s} {'begin+vsize':12s} {'fits?'}")
    for name, ndims, dimids, nc_type, vsize, begin in var_info:
        end = begin + vsize
        fits = "OK" if end <= actual_size else "BEYOND EOF!!"
        print(f"{name:20s} {nc_type:<8d} {vsize:<10d} {begin:<12d} {end:<12d} {fits}")


if __name__ == "__main__":
    main(sys.argv[1])
