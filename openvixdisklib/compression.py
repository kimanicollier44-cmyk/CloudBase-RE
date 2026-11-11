"""Compression adapter for sector streams (video seat: 'FastLZ adapters' decompress
incoming sector streams). Clean-room LZ77 sliding-window codec behind the adapter
interface a FastLZ adapter would expose. Honest scope: NOT byte-compatible FastLZ -
the interface (compress/decompress blocks) is the seat; the codec is educational."""
def compress(data: bytes) -> bytes:
    """Token format: 0x00 <literal> | 0x01 <offset:2 BE> <length:1>."""
    out = bytearray(); i = 0
    while i < len(data):
        best_len, best_off = 0, 0
        for off in range(1, min(i, 4096) + 1):
            j = i - off; k = 0
            while i + k < len(data) and k < 255 and data[j + k] == data[i + k]: k += 1
            if k > best_len: best_len, best_off = k, off
        if best_len >= 3:
            out += bytes([1]) + best_off.to_bytes(2, "big") + bytes([best_len]); i += best_len
        else:
            out += bytes([0, data[i]]); i += 1
    return bytes(out)

def decompress(blob: bytes) -> bytes:
    out = bytearray(); i = 0
    while i < len(blob):
        tag = blob[i]
        if tag == 0: out.append(blob[i + 1]); i += 2
        elif tag == 1:
            off = int.from_bytes(blob[i + 1:i + 3], "big"); ln = blob[i + 3]; start = len(out) - off
            for k in range(ln): out.append(out[start + k])
            i += 4
        else: raise ValueError("corrupt compressed stream")
    return bytes(out)

class CompressionAdapter:
    name = "lz77-cleanroom (FastLZ-adapter interface)"
    def compress_block(self, data: bytes) -> bytes: return compress(data)
    def decompress_block(self, blob: bytes) -> bytes: return decompress(blob)
    def ratio(self, data: bytes) -> float:
        return round(len(compress(data)) / len(data), 4) if data else 1.0
