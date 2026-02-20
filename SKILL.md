# Auto Cut + Telop Burn (MP4)

## What it does
- Accepts an MP4 file path or a direct MP4 URL.
- Transcribes speech with timestamps.
- Detects silences and cuts them (tempo-up).
- Remaps subtitles to the cut timeline.
- Burns subtitles into the final MP4.

## Inputs
- --input: local mp4 path OR direct mp4 URL (must end with .mp4)
- --lang: transcription language (default: ja)
- --silence: silence threshold seconds to remove (default: 0.6)
- --keep-pad: keep seconds before/after each cut (default: 0.15)
- --max-line: max characters per subtitle line (default: 18)

## Outputs (output/)
- final_burned.mp4
- subtitles.srt
- cut_list.csv
- transcript.txt
- original.mp4 (if downloaded)

## Usage
bash run.sh --input "<PATH_OR_DIRECT_MP4_URL>" --lang ja --silence 0.6 --keep-pad 0.15 --max-line 18

## Notes (important)
- This skill only auto-downloads when the URL is a direct MP4 file link.
- For Instagram/YouTube page URLs, upload the MP4 yourself, or provide a direct MP4 link you have rights to use.
