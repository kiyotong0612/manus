import argparse
import csv
import json
import re
import subprocess
from typing import Dict, List, Tuple

Sil = Tuple[float, float]  # (start, end) silence interval
Keep = Tuple[float, float]  # (start, end) kept interval

SIL_RE_START = re.compile(r"silence_start:\s*([0-9.]+)")
SIL_RE_END = re.compile(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)")


def run_silencedetect(input_mp4: str, noise_db: str = "-30dB", min_silence: float = 0.3) -> List[Sil]:
    cmd = ["ffmpeg", "-i", input_mp4, "-af", f"silencedetect=noise={noise_db}:d={min_silence}", "-f", "null", "-"]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    silences: List[Sil] = []
    cur_start = None
    assert p.stderr is not None
    for line in p.stderr:
        m1 = SIL_RE_START.search(line)
        if m1:
            cur_start = float(m1.group(1))
        m2 = SIL_RE_END.search(line)
        if m2 and cur_start is not None:
            end = float(m2.group(1))
            silences.append((cur_start, end))
            cur_start = None
    p.wait()
    return silences


def merge_intervals(intervals: List[Tuple[float, float]], eps: float = 1e-6) -> List[Tuple[float, float]]:
    if not intervals:
        return []
    intervals = sorted(intervals)
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        ps, pe = merged[-1]
        if s <= pe + eps:
            merged[-1] = (ps, max(pe, e))
        else:
            merged.append((s, e))
    return merged


def invert_to_keep(
    duration: float, silences: List[Sil], silence_threshold: float, keep_pad: float
) -> Tuple[List[Keep], List[Tuple[float, float]]]:
    # We only REMOVE silences longer than threshold.
    cuts = []
    for s, e in silences:
        if (e - s) >= silence_threshold:
            cuts.append((max(0.0, s - keep_pad), min(duration, e + keep_pad)))
    cuts = merge_intervals(cuts)

    keep: List[Keep] = []
    cur = 0.0
    for cs, ce in cuts:
        if cs > cur:
            keep.append((cur, cs))
        cur = max(cur, ce)
    if cur < duration:
        keep.append((cur, duration))

    keep = [(s, e) for s, e in keep if (e - s) > 0.05]
    return keep, cuts


def get_duration(input_mp4: str) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            input_mp4,
        ],
        text=True,
    ).strip()
    return float(out)


def make_cut_video(input_mp4: str, keep: List[Keep], out_mp4: str):
    parts = []
    vlabels = []
    alabels = []
    for i, (s, e) in enumerate(keep):
        v = f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]"
        a = f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS[a{i}]"
        parts.append(v)
        parts.append(a)
        vlabels.append(f"[v{i}]")
        alabels.append(f"[a{i}]")
    concat = "".join(vlabels + alabels) + f"concat=n={len(keep)}:v=1:a=1[v][a]"
    fc = ";".join(parts + [concat])

    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            input_mp4,
            "-filter_complex",
            fc,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            out_mp4,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def to_srt_time(t: float) -> str:
    if t < 0:
        t = 0
    ms = int(round(t * 1000))
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def remap_segments_to_srt(segments: List[Dict], keep: List[Keep], out_srt: str):
    new_offsets = []
    cum = 0.0
    for s, e in keep:
        new_offsets.append((s, e, cum))
        cum += (e - s)

    lines = []
    idx = 1
    for seg in segments:
        os_, oe = seg["start"], seg["end"]
        text = (seg.get("text") or "").strip()
        if not text:
            continue

        for ks, ke, new_base in new_offsets:
            isec_s = max(os_, ks)
            isec_e = min(oe, ke)
            if isec_e <= isec_s:
                continue
            ns = new_base + (isec_s - ks)
            ne = new_base + (isec_e - ks)
            if (ne - ns) < 0.2:
                continue
            lines.append((idx, ns, ne, text))
            idx += 1

    with open(out_srt, "w", encoding="utf-8") as f:
        for i, s, e, t in lines:
            f.write(f"{i}\n{to_srt_time(s)} --> {to_srt_time(e)}\n{t}\n\n")


def write_cut_csv(cuts: List[Tuple[float, float]], out_csv: str):
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cut_start", "cut_end", "cut_duration"])
        for s, e in cuts:
            w.writerow([f"{s:.3f}", f"{e:.3f}", f"{(e - s):.3f}"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--segments", required=True)
    ap.add_argument("--silence", type=float, default=0.6)
    ap.add_argument("--keep_pad", type=float, default=0.15)
    ap.add_argument("--out_video", required=True)
    ap.add_argument("--out_srt", required=True)
    ap.add_argument("--out_csv", required=True)
    args = ap.parse_args()

    dur = get_duration(args.input)
    silences = run_silencedetect(args.input, noise_db="-30dB", min_silence=0.3)

    keep, cuts = invert_to_keep(dur, silences, args.silence, args.keep_pad)
    make_cut_video(args.input, keep, args.out_video)

    with open(args.segments, "r", encoding="utf-8") as f:
        data = json.load(f)
    segments = data.get("segments", [])

    remap_segments_to_srt(segments, keep, args.out_srt)
    write_cut_csv(cuts, args.out_csv)


if __name__ == "__main__":
    main()
