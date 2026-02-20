import argparse
import json
import os
import subprocess

from faster_whisper import WhisperModel


def extract_audio(input_mp4: str, out_wav: str):
    # 16k mono wav for STT stability
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", input_mp4, "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", out_wav],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--lang", default="ja")
    ap.add_argument("--json", required=True)
    ap.add_argument("--txt", required=True)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.json), exist_ok=True)

    wav = "work/audio.wav"
    extract_audio(args.input, wav)

    # small model for speed/cost; change to "medium" if you want higher accuracy
    model = WhisperModel("small", compute_type="int8")
    segments, _info = model.transcribe(wav, language=args.lang, vad_filter=True)

    seg_list = []
    full_text = []
    for s in segments:
        seg_list.append({"start": float(s.start), "end": float(s.end), "text": (s.text or "").strip()})
        if s.text:
            full_text.append(s.text.strip())

    with open(args.json, "w", encoding="utf-8") as f:
        json.dump({"segments": seg_list, "language": args.lang}, f, ensure_ascii=False, indent=2)

    with open(args.txt, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text).strip() + "\n")


if __name__ == "__main__":
    main()
