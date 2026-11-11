"""Council seats - Gemini Carbon 4 Extended Thinking (DECIDER) + Muse (advisor).
Names/models only, no live call. Carbon tightens a HOLD gate, never loosens;
Muse gives exactly 4 advice, never overrides. Keys: GEMINI_API_KEY / MODEL_API_KEY (names only)."""
import os
CARBON4 = {"seat": "Gemini Carbon 4 Extended Thinking", "role": "DECIDER",
           "model": "google/gemini-carbon-4-extended-pro-thinking", "provider": "Google",
           "key_env": "GEMINI_API_KEY", "thinking_default_tier": 32768, "thinking_tiers": [2048, 8192, 32768],
           "authority": "final call on protocol questions; may only TIGHTEN a HOLD gate, never loosen one",
           "method": ["MAP the NFC/NBD frame flow", "MODEL sector offsets + compression behaviour",
                      "STRESS the plan against the 10 HOLD gates", "DECIDE: proceed, tighten, or hold"]}
MUSE = {"seat": "Muse", "role": "advisor", "models": ["muse-spark-1.1", "muse-wonder-1.0"],
        "provider": "Meta", "key_env": "MODEL_API_KEY", "authority": "none",
        "rule": "exactly 4 advice; Muse is a paid seat (key creation free, usage pay-as-you-go) - never labelled free"}
def seat_status():
    return [{"seat": CARBON4["seat"], "role": CARBON4["role"], "key_present": bool(os.environ.get("GEMINI_API_KEY"))},
            {"seat": "Muse", "role": "advisor", "key_present": bool(os.environ.get("MODEL_API_KEY"))}]
def muse_advice(topic: str):
    return [f"Muse advice on {topic} #1: keep the fixture loopback-only; a real port-902 client is a separate, gated project.",
            f"Muse advice on {topic} #2: parse descriptors defensively - extent lines lie in the wild; validate sector totals before any write.",
            f"Muse advice on {topic} #3: log the NFC handshake frames; readable traces beat hex dumps when debugging (problem #12/#19).",
            f"Muse advice on {topic} #4: never let the compression adapter touch a stream it did not encode in this build."]
def carbon_decide(question: str) -> dict:
    return {"question": question, "method": CARBON4["method"], "decision": "PROCEED - lab scope only",
            "note": "Fixture + synthetic disks approved; live ESXi connection stays HELD at gates 1 and 7."}
