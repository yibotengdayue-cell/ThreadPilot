from __future__ import annotations
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED

# Pillow 用来画占位封面
from PIL import Image, ImageDraw, ImageFont

EXPORT_ROOT = Path("exports")

def make_cover(topic: str, basename: str) -> tuple[str, str]:
    """
    生成占位封面 PNG（1024x1024），返回 (本地路径, URL)
    可后续替换为你的品牌色/Logo。
    """
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    png_path = EXPORT_ROOT / f"{basename}_cover.png"

    W, H = 1024, 1024
    img = Image.new("RGB", (W, H), (20, 24, 28))  # 深灰背景
    draw = ImageDraw.Draw(img)

    # 标题行
    title = "ThreadPilot"
    sub = topic or "短视频工作流"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 尝试系统默认字体；若失败用内置字体
    try:
        # 常见 Windows 字体（如未找到会抛异常）
        font_title = ImageFont.truetype("segoeuib.ttf", 72)
        font_sub   = ImageFont.truetype("segoeui.ttf", 46)
        font_ts    = ImageFont.truetype("segoeui.ttf", 32)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub   = ImageFont.load_default()
        font_ts    = ImageFont.load_default()

    # 居中排版
    tw, th = draw.textbbox((0,0), title, font=font_title)[2:]
    sw, sh = draw.textbbox((0,0), sub,   font=font_sub)[2:]
    aw, ah = draw.textbbox((0,0), ts,    font=font_ts)[2:]

    y = H//2 - (th + sh + ah + 40)//2
    draw.text(((W-tw)//2, y), title, fill=(180, 255, 210), font=font_title)
    y += th + 20
    draw.text(((W-sw)//2, y), sub,   fill=(220, 234, 255), font=font_sub)
    y += sh + 20
    draw.text(((W-aw)//2, y), ts,    fill=(150, 160, 170), font=font_ts)

    img.save(png_path, format="PNG")
    return str(png_path), f"/exports/{png_path.name}"

def make_zip(basename: str, files: list[str]) -> tuple[str, str]:
    """
    将 files 打成一个 zip 包（UTF-8 文件名），返回 (本地路径, URL)
    """
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    zip_path = EXPORT_ROOT / f"{basename}.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for fp in files:
            p = Path(fp)
            if p.exists():
                # 存档名只放文件名，避免绝对路径
                zf.write(p, arcname=p.name)
    return str(zip_path), f"/exports/{zip_path.name}"
