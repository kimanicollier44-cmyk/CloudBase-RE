"""Readable Python errors instead of cryptic binary-SDK hex codes (video problem #19)."""
LEGACY_CODES = {1: "VIX_E_FAIL (generic)", 6: "VIX_E_NOT_FOUND", 8: "VIX_E_INVALID_ARG",
                13: "VIX_E_DISK_INVALID_SECTOR", 2000: "VIX_E_DISK_NOTOPEN", 21001: "VIX_E_NFC_HOST_ERROR"}
class VixError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code; self.legacy = LEGACY_CODES.get(code, f"code {code}")
        super().__init__(f"[VixError {code} / {self.legacy}] {message}")
class NotConnectedError(VixError):
    def __init__(self, msg="handle used before connect()"): super().__init__(2000, msg)
class InvalidSectorError(VixError):
    def __init__(self, msg="sector read/write outside the disk extent"): super().__init__(13, msg)
class AuthError(VixError):
    def __init__(self, msg="session / NFC ticket authentication failed"): super().__init__(21001, msg)
