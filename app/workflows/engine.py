from __future__ import annotations
from pathlib import Path
from datetime import datetime
import re

EXPORT_ROOT = Path("exports")

def _slug(s: str) -> str:
    s = re.sub(r"[^\w\s\-·]+", "", s, flags=re.UNICODE)
    s = re.sub(r"\s+", "-", s.strip())
    return s[:60] if s else "untitled"

def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def build_storyboard(topic: str, style: str = "street", dur: float = 15.0) -> str:
    t = topic or "男装上新"
    style_note = {
        "street": "节奏偏快、对比强、街头运动场景",
        "minimal":"留白、纯净、极简布光与转场",
        "retro":  "胶片/噪点、暖色调、复古构图",
    }.get(style, "通用风格")
    lines = [
        f"# 短视频分镜 · {t}",
        "",
        f"- 平台：TikTok（美区）",
        f"- 时长：{int(dur)}s · 3 镜头 + Hook + CTA",
        f"- 风格：{style}（{style_note}）",
        f"- 生成时间：{datetime.now():%Y-%m-%d %H:%M:%S}",
        "",
        "## 镜头 1（0–3s）· Hook",
        "- 画面：超近景展示面料/细节/甩外套/抖动对焦",
        "- 台词/字幕：**核心卖点一句话**",
        "- 声音：前奏/卡点 SFX",
        "",
        "## 镜头 2（3–8s）· 卖点快切",
        "- 画面：上身展示 + 版型/面料/价格/颜色点位卡",
        "- 字幕：**价格 + 2~3 个卖点**",
        "- 节奏：按 BPM 每 0.6–0.8s 切一张",
        "",
        "## 镜头 3（8–12s）· 场景上身",
        "- 画面：街头/地铁/球场/极简白墙/复古巷道等",
        "- 字幕：**一句气质总结**",
        "",
        "## 收尾（12–15s）· CTA",
        "- 字幕：**评论区有链接 · 今日福利**",
        "- 画面：LOGO/包装/上身定格",
        "",
        "## 标签建议",
        "- #menswear #streetwear #ootd #男装上新 #tiktokfashion",
        "",
        "——",
        "（后续：可自动生成字幕 .srt、节奏点 .json、剪映/AE 草稿等）",
    ]
    return "\n".join(lines)

def export_markdown(topic: str, content: str) -> tuple[str, str]:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    name = f"{_now_tag()}_{_slug(topic)}.md"
    file_path = EXPORT_ROOT / name
    file_path.write_text(content, encoding="utf-8")
    url = f"/exports/{name}"
    return str(file_path), url
