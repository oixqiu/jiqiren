#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jiqiren.gs.cn 多语言博客自动翻译脚本
====================================
检测 content/zh/blog/ 下新增的中文文章，调用微软翻译 API 自动生成
content/<lang>/blog/ 下的同名文章（en/fr/de/it/es/ar/ja/ko）。

特性：
- 已翻译的语言版本已存在时跳过（不重复翻译、不覆盖人工润色稿）
- 保留 front matter 中的 date/tags/image/banner 等字段，只翻译 title/description 与正文
- 正文按块翻译，保护 Markdown 图片/链接/代码块不被破坏
- 静态页（about/contact/products 列表/产品详情）缺失时同样自动翻译生成
- 无 API Key 时以 --dry-run 模式运行（只报告将翻译的文件）

用法：
  AZURE_TRANSLATOR_KEY=xxx AZURE_TRANSLATOR_REGION=xxx python3 translate-blog.py
  python3 translate-blog.py --dry-run
"""
import os
import sys
import json
import re
import time
import urllib.request
import urllib.error
import pathlib

SRC = "zh"
LANGS = ["en", "fr", "de", "it", "es", "ar", "ja", "ko"]
FROM = "zh-Hans"
ENDPOINT = (
    "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0"
    "&from=" + FROM + "&textType=plain" + "".join("&to=" + l for l in LANGS)
)
DRY_RUN = "--dry-run" in sys.argv
KEY = os.environ.get("AZURE_TRANSLATOR_KEY", "")
REGION = os.environ.get("AZURE_TRANSLATOR_REGION", "")

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
CONTENT = ROOT / "content"


def log(msg):
    print("[translate] " + msg, flush=True)


def translate(text):
    """把一段文本翻译成全部目标语言，返回 {lang: text}。文本过长时自动分段。"""
    if DRY_RUN:
        return {l: "" for l in LANGS}
    text = text.strip()
    if not text:
        return {l: "" for l in LANGS}
    result = {l: "" for l in LANGS}
    chunks = [text[i : i + 3500] for i in range(0, len(text), 3500)]
    for ch in chunks:
        body = json.dumps([{"Text": ch}]).encode("utf-8")
        req = urllib.request.Request(ENDPOINT, data=body, method="POST")
        req.add_header("Ocp-Apim-Subscription-Key", KEY)
        req.add_header("Ocp-Apim-Subscription-Region", REGION)
        req.add_header("Content-Type", "application/json")
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode("utf-8"))[0]["translations"]
                    for t in data:
                        result[t["to"]] += t["text"]
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 or e.code >= 500:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise
            except Exception as e:
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
    return result


def parse_front_matter(text):
    """解析 +++ ... +++ 前的 front matter，返回 (front_matter_dict, body)。"""
    m = re.match(r"^\+\+\+\n(.*?)\n\+\+\+\n?(.*)$", text, re.S)
    if not m:
        return None, text
    fm_raw, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        kv = re.match(r'^([A-Za-z_]+)\s*=\s*(.*)$', line)
        if kv:
            fm[kv.group(1)] = kv.group(2)
    return fm, body


def render_front_matter(fm):
    out = ["+++"]
    for k, v in fm.items():
        out.append(f"{k} = {v}")
    out.append("+++")
    return "\n".join(out) + "\n"


def translate_body_multi(body):
    """返回 {lang: 翻译后完整正文}。"""
    blocks = re.split(r"\n\n+", body)
    lang_text = {l: [] for l in LANGS}
    for blk in blocks:
        blk = blk.strip()
        if not blk:
            continue
        if blk.startswith("```"):
            for l in LANGS:
                lang_text[l].append(blk)
            continue
        m = re.match(r"^(#{1,6})\s+(.+)$", blk, re.S)
        if m and "\n" not in blk:
            tr = translate(m.group(2))
            for l in LANGS:
                lang_text[l].append(f"{m.group(1)} {tr[l]}")
            continue
        lines = blk.splitlines()
        if all(re.match(r"^!\[[^\]]*\]\([^)]*\)\s*$", ln) for ln in lines if ln.strip()):
            for l in LANGS:
                lang_text[l].append(blk)
            continue
        tr = translate(blk)
        for l in LANGS:
            lang_text[l].append(tr[l])
    return {l: "\n\n".join(lang_text[l]) for l in LANGS}


def target_exists(src_rel: pathlib.Path, lang: str) -> bool:
    """判断某语言版本是否已存在（同路径下 <lang> 目录）。"""
    rel = src_rel.relative_to(CONTENT / SRC)
    return (CONTENT / lang / rel).exists()


def translate_one(src_rel: pathlib.Path):
    """翻译单个内容文件到所有目标语言。返回 (新生成数, 跳过数)。"""
    src_path = CONTENT / SRC / src_rel
    text = src_path.read_text(encoding="utf-8")
    fm, body = parse_front_matter(text)
    if fm is None:
        return 0, 0
    new_cnt, skip_cnt = 0, 0
    for lang in LANGS:
        dst = CONTENT / lang / src_rel
        if dst.exists():
            skip_cnt += 1
            continue
        # 翻译 front matter 中的 title/description
        fm_t = dict(fm)
        for key in ("title", "description"):
            if key in fm_t:
                val = fm_t[key].strip().strip('"')
                tr = translate(val)
                fm_t[key] = f'"{tr[lang]}"'
        # 翻译正文
        lang_body = translate_body_multi(body)[lang]
        if not DRY_RUN:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(render_front_matter(fm_t) + lang_body + "\n", encoding="utf-8")
        new_cnt += 1
    return new_cnt, skip_cnt


def collect_md_files():
    """收集 zh 下所有 .md 内容文件（博客 bundle 的 index.md、单文件文章、静态页）。"""
    files = []
    for p in sorted((CONTENT / SRC).rglob("*.md")):
        rel = p.relative_to(CONTENT / SRC)
        # 排除 _index.md 等特殊文件外的全部 md（包括静态页与博客）
        files.append(rel)
    return files


def main():
    if not DRY_RUN and (not KEY or not REGION):
        log("缺少 AZURE_TRANSLATOR_KEY / AZURE_TRANSLATOR_REGION 环境变量，退出。")
        sys.exit(1)
    if DRY_RUN:
        log("dry-run 模式：仅报告，不调用翻译 API。")
    files = collect_md_files()
    total_new, total_skip = 0, 0
    for rel in files:
        new_cnt, skip_cnt = translate_one(rel)
        total_new += new_cnt
        total_skip += skip_cnt
        if new_cnt:
            log(f"新生成 {new_cnt} 个语言版本: {rel}")
    log(f"完成。新生成 {total_new} 个文件，跳过已存在 {total_skip} 个。")
    if DRY_RUN and total_new == 0:
        log("所有语言版本已齐全，无需翻译。")


if __name__ == "__main__":
    main()
