from __future__ import annotations
import json

def build_beats_json(bpm: int = 120, duration: float = 15.0) -> str:
    """
    生成节拍点（单位：秒），默认 120 BPM，总时长 15s。
    剪辑时可按这些拍点去切镜/上字幕。
    """
    interval = 60.0 / max(bpm, 1)
    t = 0.0
    beats = []
    while t <= duration + 1e-6:
        beats.append(round(t, 3))
        t += interval
    return json.dumps({"bpm": bpm, "duration": duration, "beats": beats}, ensure_ascii=False, indent=2)
