from __future__ import annotations
import json, base64, time, argparse
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

ROOT = Path(__file__).resolve().parent
PRIV = ROOT / "private_key.pem"
PUB  = ROOT / "public_key.pem"

def canonical_json(d: dict) -> bytes:
    d = {k: v for k, v in d.items() if k != "sig"}
    return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

def gen_keypair():
    if PRIV.exists() or PUB.exists():
        raise SystemExit("Keys already exist; aborting.")
    sk = Ed25519PrivateKey.generate()
    pk = sk.public_key()
    PRIV.write_bytes(
        sk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    PUB.write_bytes(
        pk.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    print(f"Generated:\n  {PRIV}\n  {PUB}")

def make_license(days: int, plan: str, features: list[str], hwid: str | None, major: int | None):
    if not PRIV.exists():
        raise SystemExit("private_key.pem not found; run with --gen-keys first.")
    sk = serialization.load_pem_private_key(PRIV.read_bytes(), password=None)
    payload = {
        "exp": int(time.time()) + days*24*3600,
        "plan": plan,
        "features": features,
    }
    if hwid:
        payload["hwid"] = hwid
    if major is not None:
        payload["major"] = int(major)

    msg = canonical_json(payload)
    sig = sk.sign(msg)
    payload["sig"] = base64.b64encode(sig).decode("ascii")
    blob = base64.b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")).decode("ascii")
    print(blob)

def main():
    ap = argparse.ArgumentParser(description="ThreadPilot offline keygen")
    ap.add_argument("--gen-keys", action="store_true", help="Generate Ed25519 keypair")
    ap.add_argument("--days", type=int, help="License duration in days")
    ap.add_argument("--plan", default="pro")
    ap.add_argument("--features", default="ai,plugins")
    ap.add_argument("--hwid", default=None)
    ap.add_argument("--major", type=int, default=None)
    args = ap.parse_args()

    if args.gen_keys:
        gen_keypair(); return
    if args.days:
        feats = [s for s in (args.features or "").split(",") if s]
        make_license(args.days, args.plan, feats, args.hwid, args.major); return
    ap.print_help()

if __name__ == "__main__":
    main()
