# Changelog

## v1.0.0 - 2026-11-11
- Clean-room Python study of the OpenVixDiskLib / VDDK concept from Darion's Gemini study doc
- Real: VMDK descriptor parser + synthetic disk creator; NBD protocol codec (public spec, 28-byte request structs) + loopback lab fixture server/client; VixDiskLibHandle API (connect/open/read/write/get_info) with sector bounds checks; LZ77 compression adapter (FastLZ-interface seat, not byte-compatible)
- Modelled, honestly labelled: NFC greeting/auth framing; vCenter session + NFC ticket (offline, credential env names only)
- Council: Gemini Carbon 4 Extended Thinking (DECIDER) + Muse (advisor)
- Full study catalogue: 20 problems + 20 reasons in openvixdisklib/problems.py; 10 HOLD gates
- Verified: demo CHECKS 12/12, pytest 11 passed
