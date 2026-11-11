"""vCenter session + NFC ticket model (video step 1: Inventory & Session Login).
Real flow modelled: SOAP/pyVmomi login -> session token -> NFC ticket for a disk lease.
THIS build runs the model OFFLINE against the lab fixture - no vCenter is contacted,
credentials are env NAMES only (VCENTER_USER / VCENTER_PASSWORD), never read here."""
import hashlib, os, time
class SessionTicket:
    def __init__(self, host: str, user: str):
        self.host = host; self.user = user
        self.session_token = hashlib.sha256(f"{host}|{user}|{time.time()}".encode()).hexdigest()[:32]
        self.created = int(time.time())
    def nfc_ticket(self, datastore_path: str) -> dict:
        """An NFC lease ticket: host, port 902, SSL thumbprint placeholder, disk path."""
        return {"host": self.host, "port": 902, "datastore_path": datastore_path,
                "ticket_id": hashlib.sha256((self.session_token + datastore_path).encode()).hexdigest()[:16],
                "ssl_thumbprint": "LAB:FI:XT:UR:E0:00", "expires_in_s": 300}
def login(host: str, user: str | None = None) -> SessionTicket:
    user = user or os.environ.get("VCENTER_USER", "lab-user")
    if os.environ.get("VCENTER_PASSWORD"):
        pass  # presence only - the value is never read, stored, or sent by this build
    return SessionTicket(host, user)
