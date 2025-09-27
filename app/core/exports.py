from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import List, Dict

EXPORT_DIR = Path("exports")

def list_recent_json(limit: int = 10) -> List[Dict]:
    """
    扫描 exports 目录，把同一次导出的相关文件（md/srt/json/png/zip 等）
    以“同名基底”分组，并按最新修改时间倒序返回前 N 条。
    """
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    files = [p for p in EXPORT_DIR.glob("*") if p.is_file()]

    groups: Dict[str, Dict] = {}
    for f in files:
        base = f.stem  # 去掉扩展名后的“基底”
        ext = f.suffix.lstrip(".").lower()
        mt  = f.stat().st_mtime

        if base not in groups:
            groups[base] = {
                "base": base,
                "mtime": mt,
                "files": {}
            }
        groups[base]["files"][ext] = f.name
        if mt > groups[base]["mtime"]:
            groups[base]["mtime"] = mt

    items = []
    for g in groups.values():
        items.append({
            "base": g["base"],
            "mtime": datetime.fromtimestamp(g["mtime"]).strftime("%Y-%m-%d %H:%M:%S"),
            "links": {ext: f"/exports/{name}" for ext, name in g["files"].items()}
        })

    items.sort(key=lambda x: x["mtime"], reverse=True)
    return items[:limit]
