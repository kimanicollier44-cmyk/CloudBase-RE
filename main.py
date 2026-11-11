"""OpenVixDiskLib demo: synthetic VMDK -> session/NFC ticket -> NFC handshake model
-> NBD loopback stream -> sector write/read verified -> compression adapter -> council.
Run:  python3 main.py demo     (or just: python3 main.py)"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openvixdisklib import __version__, council, gates, nbd, nfc, problems, session
from openvixdisklib.compression import CompressionAdapter
from openvixdisklib.handles import ConnectParams, VixDiskLibHandle
from openvixdisklib.vmdk import SECTOR, create_synthetic_disk, parse_descriptor

def demo() -> int:
    checks = []
    def check(name, ok): checks.append((name, bool(ok)))
    print(f"=== CloudBase-RE v{__version__} demo - OpenVixDiskLib clean-room study ===")
    tmp = tempfile.mkdtemp(prefix="vixlab-")
    dpath, fpath, sectors = create_synthetic_disk(os.path.join(tmp, "labdisk"), size_mb=1)
    desc = open(dpath).read()
    info = parse_descriptor(desc)
    check("descriptor: 1 extent, monolithicFlat, lsilogic", len(info["extents"]) == 1 and info["create_type"] == "monolithicFlat" and info["ddb"].get("adapterType") == "lsilogic")
    check("descriptor: sector total matches created size", info["total_sectors"] == sectors)
    print(f"disk: {info['capacity_bytes']/1048576:.0f} MiB, {sectors} sectors, extent {info['extents'][0]['file']}")
    sess = session.login("lab-vcenter.local")
    ticket = sess.nfc_ticket("[lab-datastore] labdisk.vmdk")
    check("session: token + NFC ticket issued (port 902)", len(sess.session_token) == 32 and ticket["port"] == 902)
    print(f"session: user={sess.user} ticket={ticket['ticket_id']} -> {ticket['host']}:902")
    op, body = nfc.decode_frame(nfc.encode_frame(nfc.OP_AUTH, nfc.auth_payload(ticket["ticket_id"])))
    check("NFC codec: auth frame round-trips", op == nfc.OP_AUTH and ticket["ticket_id"].encode() in body)
    h = VixDiskLibHandle().connect(ConnectParams(transport="fixture"))
    h.open(desc)
    gi = h.get_info()
    check("handle: info matches descriptor", gi["capacity_sectors"] == sectors and gi["transport"] == "fixture")
    pattern = bytes(range(256)) * 2  # exactly 1 sector
    h.write(10, pattern)
    back = h.read(10, 1)
    check("NBD stream: sector 10 write->read identical", back == pattern)
    check("NBD stream: sector 11 still zero", h.read(11, 1) == b"\x00" * SECTOR)
    h.close()
    adapter = CompressionAdapter()
    blob = adapter.compress_block(back * 8)
    check("compression: round-trip + smaller on repetitive data", adapter.decompress_block(blob) == back * 8 and len(blob) < len(back * 8))
    print(f"compression: {adapter.name}, ratio on 8 repeated sectors = {adapter.ratio(back * 8)}")
    check("catalogue: 20 problems + 20 reasons from the study doc", len(problems.PROBLEMS) == 20 and len(problems.REASONS) == 20)
    seats = council.seat_status()
    check("council: 2 seats, keys presence-only", len(seats) == 2 and all(isinstance(s["key_present"], bool) for s in seats))
    check("council: Muse gives exactly 4 advice", len(council.muse_advice("OpenVixDiskLib demo")) == 4)
    check("council: Carbon 4 decides PROCEED (lab scope)", council.carbon_decide("run fixture demo?")["decision"].startswith("PROCEED"))
    print(f"HOLD gates: {len(gates.GATES)}")
    passed = sum(1 for _, ok in checks if ok)
    for n, ok in checks: print(f"  [{'PASS' if ok else 'FAIL'}] {n}")
    print(f"CHECKS: {passed}/{len(checks)}")
    return 0 if passed == len(checks) else 1

if __name__ == "__main__":
    raise SystemExit(demo())
