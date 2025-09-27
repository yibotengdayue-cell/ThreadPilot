import logging
from fastapi import HTTPException
from app.core.config import settings
from licensing.verifier import check_license

def ensure_license_or_raise():
    """在应用启动时调用；演示模式允许通过，上线可改为严格模式"""
    res = check_license(allow_demo=bool(settings.LICENSE_DEMO_OK))
    logging.getLogger("licensing").info("License status: %s", res.get("status"))
    if res.get("status") in ("invalid","expired"):
        raise HTTPException(status_code=402, detail=f"License {res.get('status')}")
    return res
