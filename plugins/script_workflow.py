from __future__ import annotations
from app.core.dispatcher import dispatcher
from app.workflows.engine import build_storyboard, export_markdown
from app.workflows.srt import build_srt
from app.workflows.tempo import build_beats_json
from app.workflows.pack import make_cover, make_zip
from pathlib import Path

def _write_export(rel_name: str, content: str) -> tuple[str, str]:
    root = Path("exports"); root.mkdir(parents=True, exist_ok=True)
    p = root / rel_name
    p.write_text(content, encoding="utf-8")
    return str(p), f"/exports/{p.name}"

def _parse_kv(args: list[str]) -> tuple[str, dict]:
    """
    将末尾的 key=value 提取为字典，其余拼为主题：
    示例：["美式宽松卫衣","style=street","bpm=140","dur=12","lang=en"]
    -> topic="美式宽松卫衣", opts={"style":"street","bpm":"140","dur":"12","lang":"en"}
    """
    kv = {}
    tokens = []
    for x in args:
        if "=" in x:
            k, v = x.split("=", 1)
            kv[k.strip().lower()] = v.strip()
        else:
            tokens.append(x)
    topic = " ".join(tokens).strip() or "男装上新"
    return topic, kv

@dispatcher.register("scriptwf", "生成分镜+字幕+节奏点+封面并打包（用法：/scriptwf 主题… [style=street|minimal|retro] [bpm=120] [dur=15] [lang=zh|en]）")
def _scriptwf(ctx, args):
    topic, kv = _parse_kv(args)
    style = kv.get("style","street").lower()
    lang  = kv.get("lang","zh").lower()
    try:
        bpm   = int(kv.get("bpm","120"))
    except:
        bpm = 120
    try:
        dur   = float(kv.get("dur","15"))
    except:
        dur = 15.0

    # 1) 分镜（带风格/时长信息）
    md = build_storyboard(topic, style=style, dur=dur)
    md_path, md_url = export_markdown(topic, md)
    base = Path(md_path).with_suffix("").name

    # 2) 字幕（按风格/语言/时长拉伸）
    srt_text = build_srt(style=style, lang=lang, duration=dur)
    srt_path, srt_url = _write_export(base + ".srt", srt_text)

    # 3) 节奏点（按 bpm/dur）
    beats_json = build_beats_json(bpm=bpm, duration=dur)
    beats_path, beats_url = _write_export(base + ".beats.json", beats_json)

    # 4) 封面 PNG
    cover_path, cover_url = make_cover(topic, base)

    # 5) 打成 ZIP
    zip_path, zip_url = make_zip(base, [md_path, srt_path, beats_path, cover_path])

    # 页面输出
    return (f"工作流完成：{topic}（style={style}, bpm={bpm}, dur={int(dur)}, lang={lang}）", [
        {"title":"分镜（Markdown）","text": md_path,   "link": md_url},
        {"title":"字幕（SRT）","text": srt_path,       "link": srt_url},
        {"title":"节奏点（JSON）","text": beats_path,   "link": beats_url},
        {"title":"封面（PNG）","text": cover_path,     "link": cover_url},
        {"title":"打包下载（ZIP）","text": zip_path,    "link": zip_url},
        {"title":"预览 · 分镜","code": md},
        {"title":"预览 · 节奏点","code": beats_json},
    ])
