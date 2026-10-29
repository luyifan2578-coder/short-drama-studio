"""Audit a short-drama prompt against the current formal asset directory.

Usage:
  python studio_asset_audit.py --assets PROJECT/资产 --prompt PROMPT.txt

The prompt must contain 【正式参考资产】 followed by one exact filename stem per
line, ending at the next 【...】 heading. This script checks mechanical naming
rules only; it cannot prove semantic asset selection or video quality.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
REFERENCE = re.compile(r"【正式参考资产】(?P<body>.*?)(?=【|\Z)", re.S)
QUOTED = re.compile(r"“[^”]*”|‘[^’]*’|\"[^\"]*\"", re.S)
IMAGE_NAME = re.compile(r"\.(?:png|jpg|jpeg|webp)\b", re.I)
PATH_PREFIX = re.compile(r"(?:资产|assets)[/\\]", re.I)


def inventory(asset_root: Path) -> tuple[set[str], set[str], list[str]]:
    stems: set[str] = set()
    people: set[str] = set()
    duplicate: list[str] = []
    for path in asset_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        if "待修" in path.stem or "初稿" in path.stem:
            continue
        if path.stem in stems:
            duplicate.append(path.stem)
        stems.add(path.stem)
        for folder in path.parent.parts:
            match = re.fullmatch(r"A\d+([A-Za-z]+)", folder)
            if match:
                people.add(match.group(1))
    return stems, people, duplicate


def audit(asset_root: Path, prompt: str) -> tuple[list[str], int]:
    errors: list[str] = []
    stems, people, duplicate = inventory(asset_root)
    if duplicate:
        errors.append("资产主体重名，无法唯一绑定：" + "、".join(sorted(set(duplicate))))
    if PATH_PREFIX.search(prompt):
        errors.append("提示词正文含资产路径；默认口径只写文件名主体")
    if IMAGE_NAME.search(prompt):
        errors.append("提示词正文含图片扩展名；默认口径只写文件名主体")

    reference = REFERENCE.search(prompt)
    declared: set[str] = set()
    if not reference:
        errors.append("缺少【正式参考资产】清单")
    else:
        for line in reference.group("body").splitlines():
            name = line.strip().removeprefix("- ").strip()
            if not name:
                continue
            if name in {"无", "无正式资产"} and not stems:
                continue
            if name not in stems:
                errors.append(f"参考资产不是当前正式文件名主体：{name}")
            else:
                declared.add(name)
        if not declared and stems:
            errors.append("【正式参考资产】没有有效条目")

    used: set[str] = set()

    def hide_asset(match: re.Match[str]) -> str:
        used.add(match.group())
        return " " * len(match.group())

    if stems:
        pattern = re.compile("|".join(re.escape(name) for name in sorted(stems, key=len, reverse=True)))
        remainder = pattern.sub(hide_asset, prompt)
    else:
        remainder = prompt
    for name in sorted(used - declared):
        errors.append(f"正文引用未列入参考清单：{name}")
    remainder = QUOTED.sub(lambda match: " " * len(match.group()), remainder)
    for person in sorted(people):
        if re.search(rf"(?<![A-Za-z]){re.escape(person)}(?![A-Za-z])", remainder):
            errors.append(f"正文有角色简称 {person}；须逐处写对应正式资产主体")
    return errors, len(declared)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True, help="当前项目正式资产目录")
    parser.add_argument("--prompt", type=Path, required=True, help="唯一正式提示词文本文件")
    args = parser.parse_args()
    if not args.assets.is_dir():
        parser.error(f"资产目录不存在：{args.assets}")
    if not args.prompt.is_file():
        parser.error(f"提示词文件不存在：{args.prompt}")
    errors, count = audit(args.assets, args.prompt.read_text(encoding="utf-8-sig"))
    if errors:
        print("BLOCKED:\n- " + "\n- ".join(errors))
        return 1
    print(f"ASSET TEXT PASS: {count} 个正式参考资产；仍须人工核全文语义、原文及网页真实引用节点。")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
