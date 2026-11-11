import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from openvixdisklib import council, gates, nbd, nfc, problems, session
from openvixdisklib.compression import compress, decompress
from openvixdisklib.errors import InvalidSectorError, NotConnectedError
from openvixdisklib.handles import ConnectParams, VixDiskLibHandle
from openvixdisklib.vmdk import SECTOR, create_synthetic_disk, parse_descriptor

def _disk(tmp):
    d, f, s = create_synthetic_disk(os.path.join(tmp, "t"), size_mb=1)
    return open(d).read(), s
def test_descriptor_roundtrip(tmp_path):
    desc, s = _disk(str(tmp_path)); i = parse_descriptor(desc)
    assert i["total_sectors"] == s and i["ddb"]["adapterType"] == "lsilogic" and i["cid"] == "0a1b2c3d"
def test_compression_roundtrip():
    for d in (b"", b"x", b"abcabcabc" * 50, bytes(range(256))):
        assert decompress(compress(d)) == d
def test_nfc_codec():
    op, body = nfc.decode_frame(nfc.encode_frame(nfc.OP_GREET, nfc.greet_payload("esxi-lab")))
    assert op == nfc.OP_GREET and b"esxi-lab" in body
def test_nbd_structs():
    assert len(nbd.encode_request(nbd.CMD_READ, 1, 0, 512)) == 28
    magic, err, h = nbd.struct.unpack(nbd.REP_FMT, nbd.struct.pack(nbd.REP_FMT, nbd.REP_MAGIC, 0, 7))
    assert (magic, err, h) == (nbd.REP_MAGIC, 0, 7)
def test_fixture_write_read(tmp_path):
    desc, s = _disk(str(tmp_path))
    h = VixDiskLibHandle().connect(ConnectParams()); h.open(desc)
    h.write(3, b"\xAB" * SECTOR); assert h.read(3, 1) == b"\xAB" * SECTOR; h.close()
def test_file_transport(tmp_path):
    d, f, s = create_synthetic_disk(os.path.join(str(tmp_path), "t"), size_mb=1)
    h = VixDiskLibHandle().connect(ConnectParams(transport="file")); h.open(open(d).read(), flat_path=f)
    h.write(0, b"\x01" * SECTOR); assert h.read(0, 1) == b"\x01" * SECTOR; h.close()
def test_bounds(tmp_path):
    desc, s = _disk(str(tmp_path))
    h = VixDiskLibHandle().connect(ConnectParams()); h.open(desc)
    with pytest.raises(InvalidSectorError): h.read(s, 1)
    with pytest.raises(InvalidSectorError): h.write(0, b"short")
    h.close()
def test_not_connected():
    with pytest.raises(NotConnectedError): VixDiskLibHandle().open("version=1")
def test_session_ticket():
    t = session.login("vc.local", "u").nfc_ticket("[ds] a.vmdk")
    assert t["port"] == 902 and len(t["ticket_id"]) == 16
def test_catalogue_and_gates():
    assert len(problems.PROBLEMS) == 20 and len(problems.REASONS) == 20 and len(gates.GATES) == 10
def test_council():
    assert len(council.muse_advice("x")) == 4 and council.CARBON4["thinking_default_tier"] == 32768
