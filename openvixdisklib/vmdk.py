"""VMDK descriptor parsing + synthetic disk creation.
A .vmdk pair = a small text DESCRIPTOR + a data EXTENT file. Parsing the descriptor is
real and safe on any descriptor text; the disks this build creates are synthetic lab disks."""
import re
SECTOR = 512
_EXTENT = re.compile(r'^(RW|RDONLY|NOACCESS)\s+(\d+)\s+(SPARSE|FLAT|VMFS|VMFSSPARSE|SESPARSE)\s+"([^"]+)"(?:\s+(\d+))?', re.M)

def create_synthetic_disk(base_path: str, size_mb: int = 4, adapter: str = "lsilogic"):
    """Write descriptor + zeroed flat extent. Returns (descriptor_path, flat_path, sectors)."""
    sectors = size_mb * 1024 * 1024 // SECTOR
    cyl = max(1, sectors // (255 * 63))
    desc = ("# Disk DescriptorFile\nversion=1\nencoding=\"UTF-8\"\nCID=0a1b2c3d\nparentCID=ffffffff\n"
            "createType=\"monolithicFlat\"\n\n# Extent description\n"
            f'RW {sectors} FLAT "{base_path.split("/")[-1]}-flat.vmdk" 0\n\n# The Disk Data Base\n#DDB\n\n'
            f'ddb.adapterType = "{adapter}"\nddb.geometry.cylinders = "{cyl}"\n'
            'ddb.geometry.heads = "255"\nddb.geometry.sectors = "63"\n'
            f'ddb.virtualHWVersion = "14"\n')
    dpath = base_path if base_path.endswith(".vmdk") else base_path + ".vmdk"
    fpath = dpath.replace(".vmdk", "-flat.vmdk")
    open(dpath, "w").write(desc)
    with open(fpath, "wb") as f: f.truncate(sectors * SECTOR)
    return dpath, fpath, sectors

def parse_descriptor(text: str) -> dict:
    out = {"version": None, "cid": None, "parent_cid": None, "create_type": None, "extents": [], "ddb": {}}
    for line in text.splitlines():
        line = line.strip()
        m = _EXTENT.match(line)
        if m:
            out["extents"].append({"access": m.group(1), "sectors": int(m.group(2)), "type": m.group(3),
                                   "file": m.group(4), "offset": int(m.group(5) or 0)}); continue
        if "=" in line and not line.startswith("#"):
            k, v = [x.strip().strip('"') for x in line.split("=", 1)]
            if k == "version": out["version"] = int(v)
            elif k == "CID": out["cid"] = v
            elif k == "parentCID": out["parent_cid"] = v
            elif k == "createType": out["create_type"] = v
            elif k.startswith("ddb."): out["ddb"][k[4:]] = v
    out["total_sectors"] = sum(e["sectors"] for e in out["extents"])
    out["capacity_bytes"] = out["total_sectors"] * SECTOR
    return out
