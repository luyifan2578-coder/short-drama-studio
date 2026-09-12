#!/usr/bin/env python3
"""Extract body-level paragraphs from a .docx as UTF-8 text.

No third-party dependencies. Paragraph indices match python-docx
document.paragraphs numbering (direct w:p children of the body), so they line
up with project notes that cite ranges such as "paragraphs 502-512".

Usage:
    python extract_docx.py <docx> [--query TEXT] [--style STYLE]
                            [--start N] [--end N] [--out FILE]
"""
import argparse
import sys
import zipfile
import xml.etree.ElementTree as ET

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def local(tag):
    return tag.rsplit("}", 1)[-1]


def para_style(p):
    for child in p:
        if local(child.tag) == "pPr":
            for sub in child:
                if local(sub.tag) == "pStyle":
                    return sub.get(W_NS + "val")
    return None


def para_text(p):
    parts = []
    for node in p.iter():
        tag = local(node.tag)
        if tag == "t":
            parts.append(node.text or "")
        elif tag == "tab":
            parts.append("\t")
        elif tag == "br":
            parts.append("\n")
    return "".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--query")
    ap.add_argument("--style")
    ap.add_argument("--start", type=int)
    ap.add_argument("--end", type=int)
    ap.add_argument("--out")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    with zipfile.ZipFile(args.docx) as z:
        xml = z.read("word/document.xml")

    root = ET.fromstring(xml)
    body = root.find(W_NS + "body")
    paragraphs = [child for child in body if local(child.tag) == "p"]

    lines = []
    for i, p in enumerate(paragraphs, start=1):
        style = para_style(p) or ""
        text = para_text(p).strip()
        if args.style and args.style.lower() != style.lower():
            continue
        if args.query and args.query not in text:
            continue
        if args.start is not None and i < args.start:
            continue
        if args.end is not None and i > args.end:
            continue
        lines.append(f"{i}\t{style}\t{text}")

    output = "\n".join(lines)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output + "\n")
        print(f"Wrote {len(lines)} paragraphs to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
