"""Seal the studio plan before writing a prompt, then check the finished prompt.

Usage:
  python studio_preflight.py seal --source SCRIPT --assets ASSETS --plan PLAN --prompt NEW_PROMPT [--project-rules AGENTS]
  python studio_preflight.py check --source SCRIPT --assets ASSETS --plan PLAN --prompt PROMPT [--project-rules AGENTS]

This enforces order and mechanically checkable structure. Human review of story,
speech, physical continuity, visual assets, and web reference nodes remains required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from studio_asset_audit import audit


SKILL_ROOT = Path(__file__).resolve().parent.parent
SKILL_FILES = (
    SKILL_ROOT / "SKILL.md",
    SKILL_ROOT / "references/production-rules.md",
    SKILL_ROOT / "references/splitting.md",
    SKILL_ROOT / "references/video-prompt.md",
    SKILL_ROOT / "references/craft.md",
    SKILL_ROOT / "references/continuity-ledger.md",
    SKILL_ROOT / "references/validation-and-evidence.md",
    SKILL_ROOT / "scripts/studio_asset_audit.py",
    Path(__file__).resolve(),
)
FIELDS = (
    "时长", "景别", "机位/摄影机", "人物位置", "动作",
    "表演", "对白/VO", "环境与物理", "结束位置",
)
SHOT = re.compile(r"【镜头(?P<number>\d+)(?P<header>[^】]*)】")
TIME = re.compile(r"(\d{1,2}:\d{2}(?:\.\d+)?)\s*[–—－-]\s*(\d{1,2}:\d{2}(?:\.\d+)?)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory_hash(asset_root: Path) -> str:
    rows = []
    for path in sorted(asset_root.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            stat = path.stat()
            rows.append((path.relative_to(asset_root).as_posix(), stat.st_size, stat.st_mtime_ns))
    return hashlib.sha256(json.dumps(rows, ensure_ascii=False).encode("utf-8")).hexdigest()


def fingerprint(args: argparse.Namespace) -> dict[str, str]:
    paths = [args.source, args.plan, *SKILL_FILES]
    if args.project_rules:
        paths.append(args.project_rules)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("缺少输入：" + "、".join(missing))
    result = {str(path): sha256(path) for path in paths}
    result[str(args.assets)] = inventory_hash(args.assets)
    return result


def plan_errors(text: str) -> list[str]:
    errors = []
    if "九项方案" not in text:
        errors.append("缺少整集九项方案标题")
    item_patterns = {
        1: r"原文|行号|范围",
        2: r"时长|时间|秒",
        3: r"场景|光态",
        4: r"拆段|边界",
        5: r"内容|钩子|戏剧曲线",
        6: r"人物|角色",
        7: r"转场|时空|层级",
        8: r"情绪",
        9: r"取舍|决定|确认|拍板",
    }
    for number in range(1, 10):
        item = re.search(rf"(?m)^\s*{number}[.、．]\s*(.+)$", text)
        if not item:
            errors.append(f"九项方案缺第 {number} 项")
        elif not re.search(item_patterns[number], item.group(1)):
            errors.append(f"九项方案第 {number} 项标题不对应工作室要求")
    if "连续" not in text or "账本" not in text:
        errors.append("缺少连续状态账本")
    for label in ("L", "时长", "场景", "人物", "情绪", "边界", "道具"):
        if label not in text:
            errors.append(f"方案未记录 {label}")
    return errors


def to_seconds(value: str) -> float:
    minutes, rest = value.split(":", 1)
    return int(minutes) * 60 + float(rest)


def shot_errors(text: str, max_seconds: float) -> list[str]:
    errors = []
    if not re.search(r"L\d+", text):
        errors.append("提示词未标来源行号")
    if "【正式参考资产】" not in text:
        errors.append("提示词未列正式参考资产")
    if "【技术尾帧锁定信息】" not in text:
        errors.append("缺少技术尾帧锁定信息")
    shots = list(SHOT.finditer(text))
    if not shots:
        return errors + ["没有编号镜头"]
    previous_end = 0.0
    for index, match in enumerate(shots):
        number = int(match.group("number"))
        if number != index + 1:
            errors.append(f"镜头编号不连续：{number}")
        end_index = shots[index + 1].start() if index + 1 < len(shots) else len(text)
        body = text[match.end():end_index]
        timing = TIME.search(match.group("header"))
        if not timing:
            errors.append(f"镜头 {number} 未写起止秒点")
            continue
        start, end = map(to_seconds, timing.groups())
        if abs(start - previous_end) > 0.05:
            errors.append(f"镜头 {number} 起点未承接上一镜")
        if end <= start:
            errors.append(f"镜头 {number} 时长无效")
        elif end - start > 2.55 and "运镜镜头" not in match.group("header"):
            errors.append(f"镜头 {number} 超过一般镜头 2.5 秒限制；仅持续揭示剧情信息的运镜镜头可标注例外")
        previous_end = end
        for field in FIELDS:
            if not re.search(rf"(?:^|[。；\n])\s*{re.escape(field)}\s*[:：]", body):
                errors.append(f"镜头 {number} 缺 {field} 字段")
    if previous_end > max_seconds + 0.05:
        errors.append(f"单元 {previous_end:g} 秒超过设定上限 {max_seconds:g} 秒")
    if "技术尾帧" not in shots[-1].group("header"):
        errors.append("末镜不是编号技术尾帧")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("seal", "check"))
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--project-rules", type=Path)
    parser.add_argument("--max-seconds", type=float, default=30.0)
    args = parser.parse_args()
    for name in ("source", "assets", "plan", "prompt", "project_rules"):
        value = getattr(args, name)
        if value is not None:
            setattr(args, name, value.resolve())
    if args.max_seconds <= 0:
        parser.error("--max-seconds 须为正数")
    if not args.assets.is_dir():
        parser.error(f"资产目录不存在：{args.assets}")
    if not args.plan.is_file():
        parser.error(f"方案文件不存在：{args.plan}")
    errors = plan_errors(args.plan.read_text(encoding="utf-8-sig"))
    lock = args.prompt.with_name(args.prompt.name + ".studio-lock.json")
    if args.mode == "seal":
        if args.prompt.exists():
            errors.append("提示词已存在；必须先完成方案再建立新的正式稿")
        if errors:
            print("BLOCKED:\n- " + "\n- ".join(errors))
            return 1
        record = {
            "sealed_at_utc": datetime.now(timezone.utc).isoformat(),
            "prompt_path": str(args.prompt),
            "max_seconds": args.max_seconds,
            "inputs": fingerprint(args),
        }
        lock.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"PLAN SEALED: {lock}")
        return 0
    if not args.prompt.is_file():
        parser.error(f"提示词不存在：{args.prompt}")
    if not lock.is_file():
        errors.append("没有起稿前的方案封存")
    else:
        record = json.loads(lock.read_text(encoding="utf-8"))
        if record.get("prompt_path") != str(args.prompt):
            errors.append("提示词路径与方案封存目标不一致")
        if record.get("max_seconds") != args.max_seconds:
            errors.append("平台单元时长上限与封存记录不一致")
        if record.get("inputs") != fingerprint(args):
            errors.append("剧本、技能、项目规则、方案或资产已改变；重新审查后再起稿")
        if args.prompt.stat().st_mtime_ns < lock.stat().st_mtime_ns:
            errors.append("提示词文件早于方案封存")
    text = args.prompt.read_text(encoding="utf-8-sig")
    shot_issues = shot_errors(text, args.max_seconds)
    asset_issues, count = audit(args.assets, text)
    errors.extend(shot_issues + asset_issues)
    if errors:
        print("BLOCKED:\n- " + "\n- ".join(errors))
        return 1
    print(f"STUDIO STRUCTURE PASS: {count} 个正式资产；仍须人工审原文、连续状态和网页真实引用。")
    print(f"PROMPT SHA256: {sha256(args.prompt)}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        sys.exit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: {exc}")
        sys.exit(1)
