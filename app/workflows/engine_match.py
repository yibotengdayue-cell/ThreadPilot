from __future__ import annotations
from pathlib import Path
import re, json

VIDEO_EXT = {".mp4",".mov",".mkv",".avi",".m4v"}
IMAGE_EXT = {".jpg",".jpeg",".png",".webp",".bmp"}

KEY_BUCKETS = {
    "hook":    ["面料","细节","质感","甩","近景","macro","detail","fabric","stitch"],
    "selling": ["版型","落肩","压线","颜色","上身","fit","shoulder","oversize","color"],
    "scene":   ["街","地铁","球场","巷","白墙","street","subway","court","alley","white"],
}

def tokenize(s: str) -> list[str]:
    s = s.lower()
    parts = re.split(r"[^\w\u4e00-\u9fa5]+", s)
    return [p for p in parts if p]

def match_assets(root: str, topic: str, limit_per_bucket: int = 10) -> dict:
    rootp = Path(root)
    if not rootp.exists():
        return {"ok": False, "error": f"not found: {root}"}

    topic_tokens = set(tokenize(topic))
    cand = []
    for p in rootp.rglob("*"):
        if not p.is_file(): continue
        ext = p.suffix.lower()
        if ext not in VIDEO_EXT | IMAGE_EXT: continue
        name = p.stem
        toks = tokenize(name)
        score = 0
        # 主题命中
        score += sum(1 for t in toks if t in topic_tokens)
        # 关键桶命中
        bucket_hits = {b: 0 for b in KEY_BUCKETS}
        for b, kws in KEY_BUCKETS.items():
            for kw in kws:
                if kw.lower() in name.lower():
                    score += 2
                    bucket_hits[b] += 1
        cand.append({"path": str(p), "name": name, "ext": ext, "score": score, "bucket_hits": bucket_hits})

    # 分桶 TopN
    result = {}
    for b in KEY_BUCKETS:
        arr = sorted(cand, key=lambda x: (x["bucket_hits"][b], x["score"]), reverse=True)
        result[b] = arr[:limit_per_bucket]

    # 写出 JSON
    EXPORT = Path("exports"); EXPORT.mkdir(parents=True, exist_ok=True)
    out = EXPORT / f"assets_candidates_{_slug(topic)}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "json": str(out)}
