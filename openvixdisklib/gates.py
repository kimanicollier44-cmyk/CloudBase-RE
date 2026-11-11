"""HOLD gates - everything live or destructive stays OFF in this build."""
GATES = [
    ("No live ESXi/vCenter connection", "the only peer is the loopback lab fixture (127.0.0.1); dialing a real host on port 902 is not implemented"),
    ("No credential values", "VCENTER_USER / VCENTER_PASSWORD are env NAMES only; values are never read, stored, logged, or sent"),
    ("No writes to a real datastore", "sector writes land only on synthetic lab disks created by this build"),
    ("Clean-room study only", "protocol behaviour modelled from the study doc + the public NBD spec; no VMware code or binaries included or downloaded"),
    ("No SDK download bypass for production", "educational/interop research artifact - not a production backup tool and not a licensing workaround"),
    ("Compression codec honesty", "the LZ77 adapter is educational and NOT byte-compatible FastLZ; never feed it real FastLZ streams"),
    ("No pyVmomi live session", "session + NFC ticket are offline models; a real SOAP login requires the user's own vCenter and their go-ahead"),
    ("Loopback only networking", "the fixture binds 127.0.0.1 on an ephemeral port and serves exactly one connection"),
    ("Synthetic disks only", "create_synthetic_disk writes zeroed lab extents; never point the file transport at a production .vmdk"),
    ("Errors stay readable", "no raw hex codes surface to users - VixError always carries a plain-English message"),
]
def list_gates(): return [f"HOLD {i+1:02d} - {n}: {d}" for i, (n, d) in enumerate(GATES)]
