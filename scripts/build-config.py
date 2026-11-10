"""Build librechat.yaml from the template and the Pugad documents.

Usage:
  python3 scripts/build-config.py <content folder> <template> <output librechat.yaml>

Locally the content folder is ./content; on the server it is the folder
synced down from S3, which is the project's AWS integration.
"""
import pathlib
import sys

PAD = " " * 10  # same indentation as {{KNOWLEDGE}} in the template

src, tpl, out = (pathlib.Path(a) for a in sys.argv[1:4])
docs = sorted(src.glob("*.md"))
if not docs:
    sys.exit(f"No .md documents found in {src}")

text = "\n\n".join(d.read_text(encoding="utf-8").strip() for d in docs)
block = "\n".join((PAD + line) if line.strip() else "" for line in text.splitlines())

template = tpl.read_text(encoding="utf-8")
marker = PAD + "{{KNOWLEDGE}}"
if marker not in template:
    sys.exit("The template has no {{KNOWLEDGE}} line indented by 10 spaces")

out.write_text(template.replace(marker, block), encoding="utf-8")
print(f"Built {out} from {len(docs)} documents ({len(text.split())} words)")
