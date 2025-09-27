from __future__ import annotations

# 预设风格 & 文案（可自行增删）
PRESETS = {
    ("street","zh"): [
        (0.0, 3.0, "90% 的人忽略了这个版型细节"),
        (3.0, 8.0, "$199 · 双层压线 · 落肩剪裁 · 三色可选"),
        (8.0, 12.0, "谁穿谁显肩宽"),
        (12.0, 15.0, "评论区有链接 · 今天下单送同色袜"),
    ],
    ("street","en"): [
        (0.0, 3.0, "Most people miss THIS detail"),
        (3.0, 8.0, "$199 · Double stitching · Drop shoulder · 3 colors"),
        (8.0, 12.0, "Broader shoulders instantly"),
        (12.0, 15.0, "Link in comments · Free same-color socks"),
    ],
    ("minimal","zh"): [
        (0.0, 3.0, "极简、耐看、好搭"),
        (3.0, 8.0, "$199 · 匠心走线 · 高密面料"),
        (8.0, 12.0, "落肩版型 · 修饰比例"),
        (12.0, 15.0, "评论领取今日福利"),
    ],
    ("minimal","en"): [
        (0.0, 3.0, "Minimal · Timeless · Easy match"),
        (3.0, 8.0, "$199 · Craft stitching · Dense fabric"),
        (8.0, 12.0, "Drop shoulder · Better proportions"),
        (12.0, 15.0, "Claim today’s perk in comments"),
    ],
    ("retro","zh"): [
        (0.0, 3.0, "90s 复古感回潮"),
        (3.0, 8.0, "$199 · 做旧质感 · 宽松剪裁"),
        (8.0, 12.0, "上身自带随性氛围"),
        (12.0, 15.0, "评论区下单享折扣"),
    ],
    ("retro","en"): [
        (0.0, 3.0, "90s retro vibe is back"),
        (3.0, 8.0, "$199 · Washed feel · Loose cut"),
        (8.0, 12.0, "Effortless mood on body"),
        (12.0, 15.0, "Discount in comments"),
    ],
}

def _fmt(t: float) -> str:
    ms = int(round((t - int(t)) * 1000))
    s  = int(t) % 60
    m  = (int(t) // 60) % 60
    h  = int(t) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def _stretch(segs, duration: float):
    # 若时长不是 15s，按比例拉伸时间轴
    if not duration or duration == 15.0:
        return segs
    scale = duration / 15.0
    return [(round(a*scale,3), round(b*scale,3), txt) for a,b,txt in segs]

def build_srt(style: str = "street", lang: str = "zh", duration: float = 15.0) -> str:
    # 单语：直接取对应语言的预设
    if lang in ("zh","en"):
        segs = PRESETS.get((style, lang)) or PRESETS.get(("street","zh"))
        segs = _stretch(segs, duration)
        lines = []
        for i, (st, ed, text) in enumerate(segs, start=1):
            lines.append(str(i))
            lines.append(f"{_fmt(st)} --> {_fmt(ed)}")
            lines.append(text)
            lines.append("")
        return "\n".join(lines)

    # 双语：en + zh 合并成同一条字幕的两行
    if lang.lower() in ("en+zh","zh+en","bilingual","bi"):
        zh = PRESETS.get((style,"zh")) or PRESETS.get(("street","zh"))
        en = PRESETS.get((style,"en")) or PRESETS.get(("street","en"))
        zh = _stretch(zh, duration)
        en = _stretch(en, duration)
        # 对齐策略：以索引配对，不足则就近取值
        n = max(len(zh), len(en))
        lines = []
        for i in range(n):
            st_zh, ed_zh, txt_zh = zh[min(i, len(zh)-1)]
            st_en, ed_en, txt_en = en[min(i, len(en)-1)]
            st = min(st_zh, st_en); ed = max(ed_zh, ed_en)
            lines.append(str(i+1))
            lines.append(f"{_fmt(st)} --> {_fmt(ed)}")
            # 英文在上，中文在下（习惯符合美区受众 + 中文受众）
            lines.append(txt_en)
            lines.append(txt_zh)
            lines.append("")
        return "\n".join(lines)

    # 兜底：未知语言回退到中文
    return build_srt(style=style, lang="zh", duration=duration)
