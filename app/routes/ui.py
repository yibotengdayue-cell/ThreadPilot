from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.analytics.service import summarize_csv
from app.core.dispatcher import dispatcher
from pathlib import Path
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def _safe_tmp_path(filename: str) -> Path:
    return Path(f"./tmp_{Path(filename).name}")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, file: UploadFile = File(...)):
    tmp = _safe_tmp_path(file.filename)
    tmp.write_bytes(await file.read())
    pretty = json.dumps(summarize_csv(str(tmp)), ensure_ascii=False, indent=2)
    return templates.TemplateResponse("index.html", {"request": request, "result": pretty, "filename": file.filename})

@router.post("/compose", response_class=HTMLResponse)
async def compose(request: Request, message: str = Form(""), file: UploadFile | None = File(None)):
    blocks = []
    msg = (message or "").strip()
    csv_summary = None

    if file and file.filename:
        tmp = _safe_tmp_path(file.filename)
        tmp.write_bytes(await file.read())
        if Path(file.filename).suffix.lower() == ".csv":
            csv_summary = json.dumps(summarize_csv(str(tmp)), ensure_ascii=False, indent=2)

    # 先把用户输入显示出来
    if msg:
        blocks.append({"title": "你的输入", "text": msg})

    # 尝试作为命令派发
    ctx = {
        "help": dispatcher.help_text,
        "csv_summary": csv_summary
    }
    dispatched = dispatcher.dispatch(msg, ctx) if msg.startswith("/") else None
    if dispatched:
        title, out_blocks = dispatched
        blocks.append({"title": title, "text": ""})
        blocks.extend(out_blocks)
    else:
        # 普通文本 + 可选 csv 概览
        if csv_summary:
            blocks.append({"title": f"CSV 概览 · {file.filename}", "code": csv_summary})
        elif not msg:
            blocks.append({"title":"提示","text":"请输入描述，或输入 /help 查看可用命令。"})

    return templates.TemplateResponse("index.html", {"request": request, "blocks": blocks})
