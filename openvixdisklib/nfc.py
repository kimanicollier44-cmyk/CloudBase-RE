"""NFC (Network File Copy) greeting/auth framing (video step 2: Socket Handshake).
Clean-room MODEL of the greeting sequence described in the study doc - magic,
version, opcode, length-prefixed payload frames - used to negotiate with the lab
fixture before the NBD stream starts. Real ESXi NFC framing stays behind the
live-connect HOLD gate; the codec here is real, the peer is the lab fixture."""
import struct
MAGIC = b"NFC1"; VERSION = 1
OP_GREET, OP_AUTH, OP_OPEN_DISK, OP_OK, OP_ERROR = 1, 2, 3, 200, 255
_HDR = struct.Struct(">4sBBH")
def encode_frame(opcode: int, payload: bytes = b"") -> bytes:
    return _HDR.pack(MAGIC, VERSION, opcode, len(payload)) + payload
def decode_frame(buf: bytes):
    magic, ver, op, ln = _HDR.unpack(buf[:_HDR.size])
    if magic != MAGIC: raise ValueError("bad NFC frame magic")
    return op, buf[_HDR.size:_HDR.size + ln]
def greet_payload(host: str) -> bytes: return f"HELLO {host} NFC/1".encode()
def auth_payload(ticket_id: str) -> bytes: return f"TICKET {ticket_id}".encode()
