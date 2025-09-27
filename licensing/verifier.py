import json, os, time, base64, logging
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

APPDATA_DIR = os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "ThreadPilot")
LICENSE_FILE = os.path.join(APPDATA_DIR, "license.dat")
PUBLIC_KEY_FILE = os.path.join(Path(__file__).resolve().parent, "public_key.pem")

def _ensure_appdata():
    Path(APPDATA_DIR).mkdir(parents=True, exist_ok=True)

def load_license_blob() -> str | None:
    if os.path.exists(LICENSE_FILE):
        try:
            return Path(LICENSE_FILE).read_text(encoding="utf-8").strip()
        except Exception:
            return None
    return None

def save_license_blob(blob: str) -> None:
    _ensure_appdata()
    Path(LICENSE_FILE).write_text(blob.strip(), encoding="utf-8")

def parse_license(blob: str) -> dict | None:
    try:
        data = json.loads(base64.b64decode(blob.encode("utf-8")).decode("utf-8", "ignore"))
        return data
    except Exception:
        return None

def _canonical_json_bytes(d: dict) -> bytes:
    d = {k: v for k, v in d.items() if k != "sig"}
    return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

def verify_signature(data: dict) -> bool:
    try:
        sig_b64 = data.get("sig")
        if not sig_b64:
            return False
        sig = base64.b64decode(sig_b64.encode("ascii"))
        msg = _canonical_json_bytes(data)
        pub = serialization.load_pem_public_key(Path(PUBLIC_KEY_FILE).read_bytes())
        assert isinstance(pub, Ed25519PublicKey)
        pub.verify(sig, msg)
        return True
    except (InvalidSignature, Exception):
        return False

def check_license(allow_demo: bool = True) -> dict:
    logger = logging.getLogger("licensing")
    blob = load_license_blob()
    if not blob:
        if allow_demo:
            logger.warning("No license found. Running in DEMO mode.")
            return {"status":"demo","exp":None,"plan":"demo"}
        return {"status":"invalid"}

    data = parse_license(blob)
    if not data:
        return {"status":"invalid"}

    if not verify_signature(data):
        return {"status":"invalid"}

    now = int(time.time())
    exp = int(data.get("exp", 0))
    if exp and now > exp:
        return {"status":"expired","exp":exp}

    return {"status":"ok","exp":exp,"plan":data.get("plan","pro"),"features":data.get("features",[])}
