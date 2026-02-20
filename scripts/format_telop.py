import argparse
import re

TIME_RE = re.compile(r"^\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d$")


def wrap_text(text: str, max_line: int) -> str:
    # Simple Japanese wrap: break by length (no spaces)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_line:
        return text
    lines = []
    cur = ""
    for ch in text:
        cur += ch
        if len(cur) >= max_line:
            lines.append(cur)
            cur = ""
    if cur:
        lines.append(cur)
    return "\n".join(lines[:2])  # keep to 2 lines for reels readability


def process_block(block, max_line):
    if len(block) < 3:
        return block
    idx = block[0]
    tim = block[1]
    text = "\n".join(block[2:]).strip()
    text = re.sub(r"(えー+|あのー+|えっと+)\s*", "", text)
    text = wrap_text(text, max_line)
    return [idx, tim, text]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_srt", required=True)
    ap.add_argument("--max_line", type=int, default=18)
    ap.add_argument("--output_srt", required=True)
    args = ap.parse_args()

    out = []
    block = []
    with open(args.input_srt, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.strip() == "":
                if block:
                    out.extend(process_block(block, args.max_line))
                    out.append("")
                    block = []
            else:
                block.append(line)
    if block:
        out.extend(process_block(block, args.max_line))
        out.append("")

    with open(args.output_srt, "w", encoding="utf-8") as f:
        f.write("\n".join(out).strip() + "\n")


if __name__ == "__main__":
    main()
