#!/usr/bin/env python3
"""扫描仓库里的资料，生成根目录的 index.html。

用法（在仓库根目录）：
    python3 scripts/build_index.py

规则：
- 每个 .html 文件算一份「在线演示」；如果某个文件夹里有 index.html
  （比如打包好的演示 App），整个文件夹只算一份，链接到这个文件夹。
- 标题取 HTML 里的 <title>。
- 日期优先取路径里 `YYMMDD-` 开头的文件夹名（如 261117-佛学的核心 → 2026-11-17），
  否则取这个文件第一次提交到 git 的日期。
- 分类取第一层文件夹名；Before2026/ 下面按子文件夹分类并标记为旧资料。
- PDF、XMind、PPT 等也会列出来，作为「其他格式」。
"""

import html
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "TumeiCoding/tumei-channel"
BRANCH = "master"

SKIP_DIRS = {".git", ".github", "scripts", "assets", "node_modules"}
OTHER_EXTS = {".pdf": "PDF", ".xmind": "XMind", ".pptx": "PPT", ".key": "Keynote", ".md": None}

GENERIC_TITLES = {"presentation", "document", "index", "vite app", "react app", "untitled", "slides"}

OLD_CATEGORY_LABELS = {
    "ai-llm": "AI / 大模型",
    "programming": "编程",
    "security": "网络安全",
    "blockchain": "区块链",
    "self-growth": "个人成长",
}


def read_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")[:20000]
    except OSError:
        text = ""
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
    if m:
        title = " ".join(html.unescape(m.group(1)).split())
        if title and title.lower() not in GENERIC_TITLES:
            return title
    return path.stem if path.name != "index.html" else path.parent.name


def git_added_date(rel: str) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%cs", "--", rel],
            cwd=ROOT, capture_output=True, text=True, check=False,
        ).stdout.split()
        if out:
            return out[-1]
    except OSError:
        pass
    return ""


def path_date(parts) -> str:
    for p in parts:
        m = re.match(r"^(\d{2})(\d{2})(\d{2})(?:[-_ ]|$)", p)
        if m:
            return f"20{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return ""


def category(parts):
    if len(parts) <= 1:
        return "其他", False
    if parts[0] == "Before2026":
        sub = parts[1] if len(parts) > 2 else "其他"
        return OLD_CATEGORY_LABELS.get(sub, sub), True
    return parts[0], False


def strip_date_prefix(name: str) -> str:
    return re.sub(r"^\d{6}[-_ ]", "", name)


def collect():
    app_dirs = set()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        d = Path(dirpath)
        if d != ROOT and "index.html" in filenames:
            app_dirs.add(d)

    items = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        d = Path(dirpath)
        for name in sorted(filenames):
            p = d / name
            rel = p.relative_to(ROOT).as_posix()
            ext = p.suffix.lower()
            if d == ROOT:
                continue  # 根目录的 README / index.html 不算资料
            inside_app = any(a in p.parents for a in app_dirs)
            if ext == ".html":
                if inside_app and not (name == "index.html" and d in app_dirs):
                    continue
                is_app = name == "index.html"
                href = (d.relative_to(ROOT).as_posix() + "/") if is_app else rel
                kind = "HTML"
            elif ext in OTHER_EXTS and OTHER_EXTS[ext] and not inside_app:
                is_app = False
                href = rel if ext == ".pdf" else f"https://github.com/{REPO}/blob/{BRANCH}/{rel}"
                kind = OTHER_EXTS[ext]
            else:
                continue

            parts = Path(rel).parts
            cat, old = category(parts)
            title = read_title(p) if ext == ".html" else strip_date_prefix(p.stem)
            date = path_date(parts) or git_added_date(rel)
            # 演示所在的视频文件夹名（如 261117-佛学的核心），方便识别是哪期视频
            episode = ""
            if not old and len(parts) > 2:
                episode = strip_date_prefix(parts[1])
            items.append({
                "title": title,
                "href": href,
                "kind": kind,
                "category": cat,
                "old": old,
                "date": date,
                "episode": episode if episode and episode != title else "",
                "path": rel,
            })

    items.sort(key=lambda x: (x["date"] or "0000"), reverse=True)
    return items


def main():
    items = collect()
    template = (ROOT / "scripts" / "index.template.html").read_text(encoding="utf-8")
    data = json.dumps(items, ensure_ascii=False, indent=1).replace("</", "<\\/")
    out = template.replace("/*__DATA__*/[]", data)
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    n_html = sum(1 for i in items if i["kind"] == "HTML")
    print(f"index.html 已生成：{n_html} 份在线演示，{len(items) - n_html} 份其他格式资料")


if __name__ == "__main__":
    main()
