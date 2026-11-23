#!/usr/bin/env python3
"""扫描仓库里的资料，生成网站首页 index.html。

GitHub Actions 每次推送都会运行它并发布网站，index.html 不提交到仓库。
本地预览（在仓库根目录）：
    python3 网站/生成首页.py

规则：
- 每个 .html 文件算一份「在线演示」；如果某个文件夹里有 index.html
  （比如打包好的演示 App），整个文件夹只算一份，链接到这个文件夹。
- 标题取 HTML 里的 <title>。
- 日期优先取路径里 `YYMMDD-` 开头的文件夹名（如 261117-佛学的核心 → 2026-11-17），
  否则取这个文件第一次提交到 git 的日期。
- 分类取第一层文件夹名；「2026年以前/」下面按子文件夹分类并标记为旧资料。
- PDF、XMind、PPT 等也会列出来，作为「其他格式」。XMind 链接到 网站/xmind.html 在线查看。
"""

import html
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
REPO = "TumeiCoding/tumei-channel"
SITE_DIR = "网站"
OLD_DIR = "2026年以前"
BRANCH = "master"

SKIP_DIRS = {".git", ".github", SITE_DIR, "node_modules", "__pycache__"}
OTHER_EXTS = {".pdf": "PDF", ".xmind": "XMind", ".pptx": "PPT", ".key": "Keynote", ".md": None}

GENERIC_TITLES = {"presentation", "document", "index", "vite app", "react app", "untitled", "slides"}



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
    if parts[0] == OLD_DIR:
        return (parts[1] if len(parts) > 2 else "其他"), True
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
                if ext == ".pdf":
                    href = rel
                elif ext == ".xmind":
                    # 用网站里的查看页在线显示思维导图
                    href = f"{SITE_DIR}/xmind.html?file={quote(rel, safe='/')}"
                else:
                    href = f"https://github.com/{REPO}/blob/{BRANCH}/{rel}"
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
    template = (ROOT / SITE_DIR / "首页模板.html").read_text(encoding="utf-8")
    data = json.dumps(items, ensure_ascii=False, indent=1).replace("</", "<\\/")
    out = template.replace("/*__DATA__*/[]", data)
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    n_html = sum(1 for i in items if i["kind"] == "HTML")
    print(f"index.html 已生成：{n_html} 份在线演示，{len(items) - n_html} 份其他格式资料")


if __name__ == "__main__":
    main()
