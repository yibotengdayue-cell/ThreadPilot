from __future__ import annotations
from pathlib import Path
from datetime import datetime
import re, json, zipfile, random, io
from PIL import Image, ImageDraw, ImageFont

EXPORT_ROOT = Path("exports")

def _slug(s: str) -> str:
    s = re.sub(r"[^\w\s\-·]+", "", s, flags=re.UNICODE)
    s = re.sub(r"\s+", "-", s.strip())
    return s[:60] if s else "untitled"

def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def beats_json(bpm: int, duration: float) -> dict:
    step = 60.0 / max(bpm, 1)
    t = 0.0
    arr = [0.0]
    while t + step <= duration + 1e-6:
        t += step
        arr.append(round(t, 1))
    return {"bpm": bpm, "duration": float(duration), "beats": arr}

def srt_text(lang: str, hooks: list[str], ctas: list[str], duration: float) -> str:
    # 非严格 SRT，仅示例
    def to_ts(sec: float) -> str:
        h = int(sec // 3600); m = int((sec%3600)//60); s = int(sec%60); ms = int((sec - int(sec))*1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    lines = []
    t = 0.0
    idx = 1
    for h in hooks:
        lines += [str(idx), f"{to_ts(t)} --> {to_ts(min(t+2.5, duration))}", h, ""]
        t += 2.5; idx += 1
    for c in ctas:
        lines += [str(idx), f"{to_ts(t)} --> {to_ts(min(t+2.5, duration))}", c, ""]
        t += 2.5; idx += 1
    return "\n".join(lines)

def cover_png(text: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (1080, 1350), (18, 21, 19))  # 深色底
    d = ImageDraw.Draw(img)
    try:
        # 系统可能无字体，故用默认
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    d.text((40, 60), "ThreadPilot", fill=(173, 255, 177), font=font)
    d.text((40, 120), text[:40], fill=(220, 220, 220), font=font)
    img.save(path)

def storyboard_md(topic: str, style: str, bpm: int, duration: float, hook: str, cta: str) -> str:
    return "\n".join([
        f"# 短视频分镜 · {topic}",
        "", f"- 平台：TikTok（美区）",
        f"- 时长：{int(duration)}s · 3 镜头 + Hook + CTA",
        f"- 风格：{style}",
        f"- 生成时间：{datetime.now():%Y-%m-%d %H:%M:%S}",
        "", "## 镜头 1（0–3s）· Hook",
        f"- 画面：超近景/甩外套/对焦跳变",
        f"- 字幕：**{hook}**",
        "", "## 镜头 2（3–8s）· 卖点快切",
        "- 画面：上身展示 + 版型/面料/价格/颜色点位卡",
        "- 字幕：**价格 + 2~3 个卖点**",
        f"- 节奏：按 BPM={bpm} 卡点切",
        "", "## 镜头 3（8–12s）· 场景上身",
        "- 画面：街头/地铁/球场/极简白墙/复古巷道等",
        "- 字幕：**一句气质总结**",
        "", "## 收尾（12–15s）· CTA",
        f"- 字幕：**{cta}**",
        "- 画面：LOGO/包装/上身定格",
    ])

def run_single(topic: str, style: str, bpm: int, duration: float, lang: str, suffix: str = "") -> dict:
    base_title = f"{_now_tag()}_{_slug(topic)}"
    if suffix:
        base_title += f"_{suffix}"

    md = storyboard_md(topic, style, bpm, duration,
                       hook="90%的人忽略了这个版型细节",
                       cta="评论区有链接 · 今日福利")
    bj = beats_json(bpm, duration)
    srt = srt_text(lang, hooks=["核心卖点一句话"], ctas=["今天下单送同色袜"], duration=duration)

    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)

    p_md   = EXPORT_ROOT / f"{base_title}.md"
    p_json = EXPORT_ROOT / f"{base_title}.beats.json"
    p_srt  = EXPORT_ROOT / f"{base_title}.srt"
    p_png  = EXPORT_ROOT / f"{base_title}_cover.png"
    p_zip  = EXPORT_ROOT / f"{base_title}.zip"

    p_md.write_text(md, encoding="utf-8")
    p_json.write_text(json.dumps(bj, ensure_ascii=False, indent=2), encoding="utf-8")
    p_srt.write_text(srt, encoding="utf-8")
    cover_png(topic, p_png)

    with zipfile.ZipFile(p_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for p in (p_md, p_json, p_srt, p_png):
            z.write(p, arcname=p.name)

    return {
        "title": base_title,
        "files": {"md": str(p_md), "beats": str(p_json), "srt": str(p_srt), "cover": str(p_png), "zip": str(p_zip)}
    }

def run_variants(topic: str, style: str, bpm: int, duration: float, lang: str, variants: int = 3) -> dict:
    # 预设三版差异：Hook/CTA/BPM微调
    presets = [
        ("A", "显肩宽一秒出型", "下单立减 · 今日有效", bpm-6),
        ("B", "秋冬内搭王炸",   "评论区有链接 · 抢先发售", bpm),
        ("C", "面料好到离谱",   "关注收藏 · 限时免运", bpm+6),
    ]
    results = []
    for i in range(min(variants, 3)):
        suf, hk, ca, vbpm = presets[i]
        # 临时替换 hook/cta
        res = run_single(topic, style, vbpm, duration, lang, suffix=suf)
        # 覆盖刚写的 md（插入差异）
        md_path = Path(res["files"]["md"])
        md_txt = md_path.read_text(encoding="utf-8")
        md_txt = md_txt.replace("**90%的人忽略了这个版型细节**", f"**{hk}**")
        md_txt = md_txt.replace("**评论区有链接 · 今日福利**", f"**{ca}**")
        md_path.write_text(md_txt, encoding="utf-8")
        results.append(res)

    # 汇总总 ZIP
    master = EXPORT_ROOT / f"{_now_tag()}_{_slug(topic)}_ALL.zip"
    with zipfile.ZipFile(master, "w", zipfile.ZIP_DEFLATED) as z:
        for r in results:
            for k, fpath in r["files"].items():
                p = Path(fpath)
                z.write(p, arcname=f"{r['title']}/{p.name}")

    return {"variants": results, "master_zip": str(master)}
