from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routes.public import router as public_router
from app.core.license import ensure_license_or_raise
from licensing.verifier import save_license_blob
from app.routes import ui as ui_router

app = FastAPI(title="ThreadPilot", version="0.1.0")

@app.on_event("startup")
def _startup():
    ensure_license_or_raise()

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    # 避免控制台 404，把浏览器要的 /favicon.ico 指到 logo.svg
    return RedirectResponse(url="/static/logo.svg")

@app.post("/api/license/activate")
def activate(license_blob: str):
    if not license_blob or len(license_blob) < 16:
        raise HTTPException(status_code=400, detail="invalid license blob")
    save_license_blob(license_blob)
    return {"ok": True}

# API 路由
app.include_router(public_router, prefix="/api")

# Web UI 路由 + 静态资源
app.include_router(ui_router.router, prefix="")
app.mount("/static", StaticFiles(directory="static"), name="static")

import plugins.registry  # 注册内置命令（/help, /script, /csvsum）

app.mount("/exports", StaticFiles(directory="exports"), name="exports")

import plugins.script_workflow  # 注册 /scriptwf

from app.core.exports import list_recent_json

@app.get("/api/recent")
def api_recent():
    return {"items": list_recent_json(10)}
