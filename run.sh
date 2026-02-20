#!/usr/bin/env bash
set -euo pipefail

# ----------------------------
# Args
# ----------------------------
INPUT=""
LANG="ja"
SILENCE="0.6"
KEEP_PAD="0.15"
MAX_LINE="18"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --input) INPUT="$2"; shift 2 ;;
    --lang) LANG="$2"; shift 2 ;;
    --silence) SILENCE="$2"; shift 2 ;;
    --keep-pad) KEEP_PAD="$2"; shift 2 ;;
    --max-line) MAX_LINE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "${INPUT}" ]]; then
  echo "ERROR: --input is required"
  exit 1
fi

mkdir -p work output

# ----------------------------
# 1) Obtain MP4
# ----------------------------
MP4_PATH="work/input.mp4"

if [[ "${INPUT}" =~ ^https?:// ]]; then
  # Only accept direct MP4 links to avoid ToS/copyright issues.
  if [[ "${INPUT}" != *".mp4"* ]]; then
    echo "This URL doesn't look like a direct .mp4 link."
    echo "Please upload the MP4 file and pass its local path instead."
    exit 2
  fi

  echo "[1/6] Downloading direct MP4..."
  curl -L --fail --retry 3 -o "${MP4_PATH}" "${INPUT}"
  cp "${MP4_PATH}" "output/original.mp4"
else
  if [[ ! -f "${INPUT}" ]]; then
    echo "ERROR: file not found: ${INPUT}"
    exit 3
  fi
  echo "[1/6] Copying local MP4..."
  cp "${INPUT}" "${MP4_PATH}"
fi

# ----------------------------
# 2) Install deps (if needed)
# ----------------------------
echo "[2/6] Installing python deps..."
python3 -m pip install -r requirements.txt >/dev/null

# ----------------------------
# 3) Transcribe (timestamps)
# ----------------------------
echo "[3/6] Transcribing..."
python3 scripts/transcribe_faster_whisper.py \
  --input "${MP4_PATH}" \
  --lang "${LANG}" \
  --json "work/segments.json" \
  --txt "output/transcript.txt"

# ----------------------------
# 4) Silence cut + subtitle remap
# ----------------------------
echo "[4/6] Cutting silences and remapping subtitles..."
python3 scripts/silence_cut_and_remap.py \
  --input "${MP4_PATH}" \
  --segments "work/segments.json" \
  --silence "${SILENCE}" \
  --keep_pad "${KEEP_PAD}" \
  --out_video "work/cut.mp4" \
  --out_srt "work/raw_cut.srt" \
  --out_csv "output/cut_list.csv"

# ----------------------------
# 5) Format telop lines (readability)
# ----------------------------
echo "[5/6] Formatting telop lines..."
python3 scripts/format_telop.py \
  --input_srt "work/raw_cut.srt" \
  --max_line "${MAX_LINE}" \
  --output_srt "output/subtitles.srt"

# ----------------------------
# 6) Burn subtitles
# ----------------------------
echo "[6/6] Burning subtitles into video..."
# Basic readable style. You can tune Fontsize/Outline/Shadow.
ffmpeg -y -i "work/cut.mp4" \
  -vf "subtitles=output/subtitles.srt:force_style='Fontsize=42,Outline=4,Shadow=2,MarginV=60'" \
  -c:a copy "output/final_burned.mp4" >/dev/null

echo "DONE ✅ Outputs are in ./output/"
ls -la output
