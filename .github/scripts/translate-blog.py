#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jiqiren.gs.cn 多语言博客自动翻译脚本
====================================
检测 content/zh/blog/ 下新增的中文文章，调用微软翻译 API 自动生成
content/<lang>/blog/ 下的同名文章（en/fr/de/it/es/ar/ja/ko/ru）。

特性：
- 已翻译的语言版本已存在时跳过（不重复翻译、不覆盖人工润色稿）
- front matter 支持 ---（YAML）与 +++（TOML）两种格式
- 只翻译 title/description 与正文；date/tags/draft 等原样保留
- 图片不复制：翻译版正文与 image 字段中的相对图片路径，自动改写为
  指向中文站的绝对路径（/blog/年/月/文章目录/图片.jpg），全球共用同一张图
- 正文按块翻译，保护 Markdown 图片/链接/代码块不被破坏
- 无 API Key 时以 --dry-run 模式运行（只报告将翻译的文件）

用法：
  AZURE_TRANSLATOR_KEY=xxx AZURE_TRANSLATOR_REGION=southeastasia python3 translate-blog.py
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
LANGS = ["en", "fr", "de", "it", "es", "ar", "ja", "ko", "ru"]
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

# 直连，不继承系统代理（GitHub runner 无代理；本地代理会导致超时）
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


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
                with OPENER.open(req, timeout=30) as resp:
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


def split_front_matter(text):
    """同时支持 ---（YAML）与 +++（TOML）front matter。
    返回 (delimiter, fm_lines(list), body)；无 front matter 返回 (None, [], text)。"""
    m = re.match(r"^(---|\+\+\+)\n(.*?)\n\1\n?(.*)$", text, re.S)
    if not m:
        return None, [], text
    delim, fm_raw, body = m.group(1), m.group(2), m.group(3)
    return delim, fm_raw.splitlines(), body


def extract_date(fm_lines):
    """从 front matter 行中提取 date 字段的 年/月，用于拼图片绝对路径。"""
    for line in fm_lines:
        m = re.match(r'^\s*date\s*:\s*"?(\d{4})-(\d{2})', line)
        if m:
            return m.group(1), m.group(2)
        m = re.match(r'^\s*date\s*=\s*"?(\d{4})-(\d{2})', line)
        if m:
            return m.group(1), m.group(2)
    return None, None


def zh_image_base(rel_path, fm_lines):
    """中文站 bundle 的图片绝对路径前缀，如 /blog/2026/10/20261008-161530。
    仅博客 page bundle（blog/<目录名>/index.md）有此映射；其他返回 None。"""
    parts = rel_path.parts
    if parts[0] != "blog":
        return None
    if rel_path.name == "index.md":
        bundle = parts[-2]
    else:
        bundle = rel_path.stem
    year, month = extract_date(fm_lines)
    if not year:
        return None
    return f"/blog/{year}/{month}/{bundle}"


def rewrite_image_path(src_path, base):
    """相对图片路径改写为中文站绝对路径；已是绝对/HTTP 路径则原样返回。"""
    p = src_path.strip()
    if not p or p.startswith("/") or p.startswith("http") or p.startswith("#"):
        return p
    return f"{base}/{p}"


def translate_fm_lines(fm_lines, lang, base):
    """翻译 front matter 中 title/description；image 字段改写为中文站绝对路径；其余行原样。"""
    out = []
    for line in fm_lines:
        stripped = line.strip()
        mt = re.match(r'^(title\s*[:=]\s*)"(.*)"\s*$', stripped)
        if mt:
            tr = translate(mt.group(2))
            out.append(f'{mt.group(1)}"{tr[lang].replace(chr(34), chr(92) + chr(34))}"')
            continue
        md = re.match(r'^(description\s*[:=]\s*)"(.*)"\s*$', stripped)
        if md:
            tr = translate(md.group(2))
            out.append(f'{md.group(1)}"{tr[lang].replace(chr(34), chr(92) + chr(34))}"')
            continue
        mi = re.match(r'^(image\s*[:=]\s*)"?([^"]+)"?\s*$', stripped)
        if mi and base:
            out.append(f'{mi.group(1)}"{rewrite_image_path(mi.group(2), base)}"')
            continue
        out.append(line)
    return out


def rewrite_body_images(body, base):
    """把正文里 Markdown 图片的相对路径改写为中文站绝对路径。"""
    if not base:
        return body

    def repl(m):
        alt, path = m.group(1), m.group(2)
        return f"![{alt}]({rewrite_image_path(path, base)})"

    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', repl, body)


def translate_body_multi(body):
    """返回 {lang: 翻译后完整正文}。图片/代码块/纯图片段落原样保留。"""
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
    rel = src_rel.relative_to(CONTENT / SRC)
    return (CONTENT / lang / rel).exists()


def translate_one(src_rel: pathlib.Path):
    src_path = CONTENT / SRC / src_rel
    text = src_path.read_text(encoding="utf-8")
    delim, fm_lines, body = split_front_matter(text)
    if delim is None:
        return 0, 0
    base = zh_image_base(src_rel, fm_lines)
    new_cnt, skip_cnt = 0, 0
    for lang in LANGS:
        dst = CONTENT / lang / src_rel
        if dst.exists():
            skip_cnt += 1
            continue
        lang_fm = translate_fm_lines(fm_lines, lang, base)
        lang_body = rewrite_body_images(body, base)
        lang_body = translate_body_multi(lang_body)[lang]
        if not DRY_RUN:
            dst.parent.mkdir(parents=True, exist_ok=True)
            out = delim + "\n" + "\n".join(lang_fm) + "\n" + delim + "\n\n" + lang_body + "\n"
            dst.write_text(out, encoding="utf-8")
        new_cnt += 1
    return new_cnt, skip_cnt


def collect_md_files():
    files = []
    for p in sorted((CONTENT / SRC).rglob("*.md")):
        rel = p.relative_to(CONTENT / SRC)
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
