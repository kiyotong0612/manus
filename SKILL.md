name: auto-cut-telop-burn
description: auto cut silences and burn subtitles into mp4
version: 0.1.0
Auto Cut + Telop Burn (MP4)
What it does

Input: local MP4 file path OR direct MP4 URL

Transcribe with timestamps

Detect silences and cut them (tempo-up)

Remap subtitles to the cut timeline (SRT)

Burn subtitles into the final MP4

Note: This skill auto-downloads only when the URL is a direct MP4 link (e.g. ends with .mp4).
For Instagram/YouTube page URLs, please download/export the MP4 yourself and pass the local file path.

Inputs

--input : local mp4 path OR direct mp4 url

--lang : transcription language (default: ja)

--silence : silence duration threshold to remove seconds (default: 0.6)

--keep-pad : keep seconds before/after each cut (default: 0.15)

--max-line : max characters per subtitle line (default: 18)

Outputs (output/)

final_burned.mp4

subtitles.srt

cut_list.csv

transcript.txt

original.mp4 (if downloaded)

Usage

bash run.sh --input "/path/to/video.mp4"
bash run.sh --input "https://example.com/video.mp4
"
bash run.sh --input "/path/to/video.mp4" --lang ja --silence 0.6 --keep-pad 0.15 --max-line 18

Requirements

ffmpeg / ffprobe

Python 3

requirements.txt packages
