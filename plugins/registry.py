from __future__ import annotations
import os, json, re, time
from pathlib import Path

# 说明：
# 1) 这个文件被 app.main 里的 `import plugins.registry` 自动导入
# 2) 我们从 app.routes.public 拿到 dispatcher，在上面注册命令

try:
    from app.routes.public import dispatcher
except Exception as e:
    # 如果项目结构不同，这里会报错；把异常提示回到前端
    dispatcher = None

def _ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S")

def _exports_root() -> Path:
    p = Path("exports")
    p.mkdir(parents=True, exist_ok=True)
    return p

def _kv_args(parts: list[str]) -> tuple[dict, list[str]]:
    """把形如 key=value 的参数提取出来，剩下的当作关键词"""
    kv = {}
    rest = []
    for p in parts:
        m = re.match(r'^(\w+)\=(.+)$', p)
        if m:
            kv[m.group(1).lower()] = m.group(2)
        else:
            rest.append(p)
    return kv, rest

if dispatcher:

    @dispatcher.command("/help")
    def cmd_help(text: str, files: list[Path] | None = None):
        """
        /help
        显示可用命令与参数用法
        """
        help_md = (
            "可用命令：\n"
            "- **/scriptwf 主题… [style=street|minimal|retro] [bpm=120] [dur=15] [lang=zh|en|en+zh] [variants=3]**\n"
            "  生成分镜 + SRT 字幕 + 节奏点 JSON + 封面 PNG，并打包 ZIP；variants 可一键出 A/B/C 多版。\n\n"
            "- **/match root=\"盘符:\\素材路径\" 关键词…**\n"
            "  在本地素材目录中，按文件名匹配关键词，输出候选素材清单（JSON 写入 exports）。\n\n"
            "示例：\n"
            "  `/scriptwf 美式宽松卫衣 · 199USD · 秋冬上新 · 三色 style=retro bpm=100 dur=18 lang=en+zh variants=3`\n"
            "  `/match root=\"D:\\素材\" 卫衣 秋冬 上新`\n"
        )
        return {"ok": True, "message": help_md}

    @dispatcher.command("/match")
    def cmd_match(text: str, files: list[Path] | None = None):
        """
        /match root="D:\素材" 关键词…
        在给定根目录下递归扫描常见素材扩展名，按文件名包含关键词进行粗匹配，输出到 exports\assets_candidates_*.json
        """
        parts = [p for p in re.split(r"\s+", text.strip()) if p]
        kv, keywords = _kv_args(parts)

        root = kv.get("root")
        if not root:
            return {"ok": False, "message": "缺少参数：root=素材根目录 ，例如：/match root=\"D:\\素材\" 卫衣 秋冬"}

        root_path = Path(root)
        if not root_path.exists():
            return {"ok": False, "message": f"素材目录不存在：{root_path}"}

        # 支持的视频/图片/音频扩展（可按需增删）
        exts = {".mp4",".mov",".mkv",".avi",".wav",".mp3",".m4a",".aac",".flac",".jpg",".jpeg",".png",".webp",".tif",".tiff"}

        candidates: list[dict] = []
        for p in root_path.rglob("*"):
            if p.is_file() and p.suffix.lower() in exts:
                name = p.name.lower()
                hit = [kw for kw in keywords if kw.lower() in name] if keywords else []
                if (not keywords) or hit:
                    candidates.append({
                        "path": str(p),
                        "name": p.name,
                        "ext": p.suffix.lower(),
                        "size": p.stat().st_size,
                        "hit_keywords": hit,
                    })

        out = {
            "root": str(root_path),
            "keywords": keywords,
            "count": len(candidates),
            "items": candidates,
        }
        out_path = _exports_root() / f"assets_candidates_{_ts()}.json"
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

        url = f"/exports/{out_path.name}"
        msg = f"素材候选清单已生成：{out_path}（共 {len(candidates)} 条）\n点击打开：{url}"
        return {"ok": True, "message": msg}

else:
    # 兜底：如果 dispatcher 未加载，给出提示
    def noop(*args, **kwargs):
        return {"ok": False, "message": "dispatcher 未就绪，检查 app.routes.public 是否暴露 dispatcher"}
