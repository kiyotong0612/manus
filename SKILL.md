---
name: "Auto Cut + Telop Burn"
description: "MP4(ローカル/直mp4 URL) → 文字起こし → 無音カット → SRT生成 → 字幕焼き付け → mp4出力"
version: "0.1.0"
author: "Hatake"
license: "MIT"
---

# Auto Cut + Telop Burn (MP4)

## 概要
このSkillは、MP4動画（ローカルファイル or 直mp4 URL）を入力として受け取り、以下を自動で行います。

- 動画から音声を抽出
- 文字起こし（タイムコード付き）
- 無音区間の検出 → テンポよくカット
- カット後のタイムラインに合わせて字幕（SRT）を再マッピング
- 字幕を動画へ焼き付けて書き出し

> ⚠️ 注意：このSkillが自動でダウンロードできるのは **直mp4 URL（URL内に .mp4 を含む）** のみです。  
> Instagram/YouTubeなどの「ページURL」から動画を取得する処理は、権限・仕様・規約・著作権の問題で不安定/非推奨のため、**動画ファイル（mp4）をアップロードして入力**してください。

---

## 入力（Inputs）
- `--input` : ローカルのMP4ファイルパス、または **直mp4 URL**
- `--lang` : 文字起こし言語（デフォルト：`ja`）
- `--silence` : 「無音」とみなして削除対象にする秒数（デフォルト：`0.6`）
- `--keep-pad` : 無音区間の前後に残す余韻秒数（デフォルト：`0.15`）
- `--max-line` : テロップ1行あたり最大文字数（デフォルト：`18`）

---

## 出力（Outputs）
出力は `output/` に生成されます。

- `final_burned.mp4`  
  カット済み + 字幕焼き付け済みの最終動画
- `subtitles.srt`  
  カット後タイムラインに合わせた字幕ファイル
- `cut_list.csv`  
  どの区間を削除したかのログ（開始/終了/長さ）
- `transcript.txt`  
  全文文字起こし
- `original.mp4`  
  入力がURLだった場合にダウンロードした原本（任意）

---

## 使い方（Usage）

### 1) ローカルMP4を入力する（推奨）
```bash
bash run.sh --input "/path/to/video.mp4"
