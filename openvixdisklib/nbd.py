"""NBD (Network Block Device) protocol codec + a LOOPBACK lab fixture server.
NBD is a public, documented protocol (unlike the closed SDK): handshake magic,
request (magic 0x25609513) and reply (magic 0x67446698) structs are implemented for
real below. The fixture serves a synthetic flat extent on 127.0.0.1 only - it stands
in for the ESXi port-902 service so the full path can be exercised in the lab."""
import socket, struct, threading
from .errors import InvalidSectorError
from .vmdk import SECTOR
OLD_MAGIC = b"NBDMAGIC"; IHAVEOPT = struct.pack(">Q", 0x49484156454F5054)
REQ = struct.Struct(">IHHQI")   # magic, command flags/type packed by caller below
REQ_FMT = ">IIQQI"             # magic, type, handle, offset(u64), length - the real 28-byte NBD request
REP_FMT = ">IIQ"                # magic, error, handle
REQ_MAGIC = 0x25609513; REP_MAGIC = 0x67446698
CMD_READ, CMD_WRITE, CMD_DISC = 0, 1, 2

def encode_request(cmd: int, handle: int, offset: int, length: int) -> bytes:
    return struct.pack(REQ_FMT, REQ_MAGIC, cmd, handle, offset, length)
def decode_reply(buf: bytes):
    magic, err, handle = struct.unpack(REP_FMT, buf)
    if magic != REP_MAGIC: raise ValueError("bad NBD reply magic")
    return err, handle

class LabBlockServer(threading.Thread):
    """Serves one bytearray 'disk' over loopback NBD. Stops on CMD_DISC."""
    def __init__(self, disk: bytearray):
        super().__init__(daemon=True); self.disk = disk; self.port = None; self._srv = None
    def run(self):
        self._srv = socket.socket(); self._srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv.bind(("127.0.0.1", 0)); self._srv.listen(1); self.port = self._srv.getsockname()[1]
        conn, _ = self._srv.accept()
        with conn:
            conn.sendall(OLD_MAGIC + IHAVEOPT + struct.pack(">Q", len(self.disk)))
            conn.recv(8 + 4)  # client flags (simplified haggling)
            while True:
                head = conn.recv(struct.calcsize(REQ_FMT))
                if len(head) < struct.calcsize(REQ_FMT): break
                magic, cmd, handle, off, ln = struct.unpack(REQ_FMT, head)
                if magic != REQ_MAGIC or cmd == CMD_DISC: break
                if cmd == CMD_READ:
                    data = bytes(self.disk[off:off + ln])
                    conn.sendall(struct.pack(REP_FMT, REP_MAGIC, 0, handle) + data)
                elif cmd == CMD_WRITE:
                    data = b""
                    while len(data) < ln: data += conn.recv(ln - len(data))
                    self.disk[off:off + ln] = data
                    conn.sendall(struct.pack(REP_FMT, REP_MAGIC, 0, handle))
        self._srv.close()

class NbdClient:
    def __init__(self): self.sock = None; self.export_size = 0; self._handle = 0
    def connect(self, host: str, port: int):
        self.sock = socket.create_connection((host, port), timeout=10)
        greet = self.sock.recv(8 + 8 + 8)
        if not greet.startswith(OLD_MAGIC): raise ValueError("not an NBD server greeting")
        self.export_size = struct.unpack(">Q", greet[16:24])[0]
        self.sock.sendall(struct.pack(">Q", 1) + struct.pack(">I", 0))  # fixed newstyle flags
        return self
    def _next(self): self._handle += 1; return self._handle
    def read(self, offset: int, length: int) -> bytes:
        h = self._next(); self.sock.sendall(encode_request(CMD_READ, h, offset, length))
        rep = self.sock.recv(struct.calcsize(REP_FMT)); err, _ = decode_reply(rep)
        if err: raise InvalidSectorError(f"NBD read error {err} at offset {offset}")
        data = b""
        while len(data) < length: data += self.sock.recv(length - len(data))
        return data
    def write(self, offset: int, data: bytes):
        h = self._next(); self.sock.sendall(encode_request(CMD_WRITE, h, offset, len(data)) + data)
        rep = self.sock.recv(struct.calcsize(REP_FMT)); err, _ = decode_reply(rep)
        if err: raise InvalidSectorError(f"NBD write error {err} at offset {offset}")
    def close(self):
        try: self.sock.sendall(encode_request(CMD_DISC, 0, 0, 0)); self.sock.close()
        except Exception: pass
