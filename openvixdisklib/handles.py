"""VixDiskLib-style handle API (video: 'Emulates VDDK Interfaces' - VixDiskLibHandle
with connect / open / read / write signatures mirroring the native SDK).
Sector-addressed like the real API: read/write take a start sector + sector count.
Transports: 'file' (a local synthetic flat extent) and 'fixture' (NFC handshake model
+ NBD stream to the loopback lab server). No live ESXi transport exists in this build."""
from .errors import NotConnectedError, InvalidSectorError
from .nbd import LabBlockServer, NbdClient
from .vmdk import SECTOR, parse_descriptor
from . import nfc

class ConnectParams:
    def __init__(self, server: str = "lab-fixture", user: str = "lab-user", transport: str = "fixture"):
        self.server, self.user, self.transport = server, user, transport

class VixDiskLibHandle:
    def __init__(self):
        self._conn = None; self._client = None; self._server = None
        self._file = None; self._info = None; self.handshake_log = []
    def connect(self, params: ConnectParams):
        self._conn = params; return self
    def open(self, descriptor_text: str, flat: bytes | bytearray | None = None, flat_path: str | None = None):
        if self._conn is None: raise NotConnectedError()
        self._info = parse_descriptor(descriptor_text)
        if self._conn.transport == "fixture":
            disk = bytearray(flat if flat is not None else b"\x00" * self._info["capacity_bytes"])
            self._server = LabBlockServer(disk); self._server.start()
            import time
            while self._server.port is None: time.sleep(0.01)
            # NFC handshake MODEL: greeting + ticket auth frames (codec round-trip)
            for op, payload in ((nfc.OP_GREET, nfc.greet_payload(self._conn.server)),):
                op2, body = nfc.decode_frame(nfc.encode_frame(op, payload))
                self.handshake_log.append(f"NFC op {op2}: {body.decode()}")
            self._client = NbdClient().connect("127.0.0.1", self._server.port)
            self._disk = disk
        else:
            self._file = open(flat_path, "r+b")
        return self
    def get_info(self) -> dict:
        if self._info is None: raise NotConnectedError("no disk open")
        return {"capacity_sectors": self._info["total_sectors"], "capacity_bytes": self._info["capacity_bytes"],
                "create_type": self._info["create_type"], "extents": len(self._info["extents"]),
                "adapter": self._info["ddb"].get("adapterType"), "transport": self._conn.transport}
    def _bounds(self, start_sector: int, count: int):
        if start_sector < 0 or start_sector + count > self._info["total_sectors"]:
            raise InvalidSectorError(f"sectors {start_sector}..{start_sector + count} outside 0..{self._info['total_sectors']}")
    def read(self, start_sector: int, count: int) -> bytes:
        self._bounds(start_sector, count)
        off, ln = start_sector * SECTOR, count * SECTOR
        if self._client: return self._client.read(off, ln)
        self._file.seek(off); return self._file.read(ln)
    def write(self, start_sector: int, data: bytes):
        if len(data) % SECTOR: raise InvalidSectorError("writes must be whole sectors (512-byte multiples)")
        self._bounds(start_sector, len(data) // SECTOR)
        off = start_sector * SECTOR
        if self._client: self._client.write(off, data)
        else: self._file.seek(off); self._file.write(data); self._file.flush()
    def close(self):
        if self._client: self._client.close(); self._client = None
        if self._file: self._file.close(); self._file = None
