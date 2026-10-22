#!/usr/bin/env python3
"""Check README language navigation, links and preserved technical examples."""

import html
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = json.loads((ROOT / "docs/languages.json").read_text())
START = "<!-- language-navigation:start -->"
END = "<!-- language-navigation:end -->"


def filename(code):
    return "README" + ("" if code == "en" else "." + code) + ".md"


def navigation():
    links = [
        f'<a href="{filename(item["code"])}" lang="{item["code"]}" '
        f'dir="{item.get("dir", "ltr")}">{html.escape(item["label"])}</a>'
        for item in LANGUAGES
    ]
    rows = [" · ".join(links[index : index + 8]) for index in range(0, len(links), 8)]
    return START + '\n<p dir="ltr">\n' + "<br>\n".join(rows) + "\n</p>\n" + END


def fenced(text):
    return re.findall(r"^```.*?^```", text, re.MULTILINE | re.DOTALL)


def inline_code(text):
    text = re.sub(r"^```.*?^```", "", text, flags=re.MULTILINE | re.DOTALL)
    return Counter(re.findall(r"`([^`\n]+)`", text))


def markdown_links(text):
    return re.findall(r"\]\(([^\s)]+)\)", text)


def main():
    expected = {filename(item["code"]) for item in LANGUAGES}
    actual = {path.name for path in ROOT.glob("README*.md")}
    errors = []
    if actual != expected:
        errors.append(f"README language files differ: {sorted(actual ^ expected)}")
    source = (ROOT / "README.md").read_text()
    nav = navigation()
    technical_links = set(markdown_links(source)) - expected
    for item in LANGUAGES:
        name = filename(item["code"])
        path = ROOT / name
        if not path.exists():
            continue
        text = path.read_text()
        if text.count(START) != 1 or text.count(END) != 1 or nav not in text:
            errors.append(f"{name}: navigation differs from docs/languages.json")
        if "@@" in text or text.count("```") != source.count("```"):
            errors.append(f"{name}: unresolved placeholder or unbalanced code fences")
        if fenced(text) != fenced(source):
            errors.append(f"{name}: code examples differ from English")
        if item["code"] != "en":
            if inline_code(text) != inline_code(source):
                errors.append(f"{name}: inline commands or identifiers differ")
            if not technical_links <= set(markdown_links(text)):
                errors.append(f"{name}: a source documentation link is missing")
            if text.count("\n## ") != source.count("\n## "):
                errors.append(f"{name}: a source section is missing")
        for link in markdown_links(text):
            parsed = urlsplit(link)
            if not parsed.scheme and not parsed.netloc and parsed.path:
                if not (ROOT / unquote(parsed.path)).exists():
                    errors.append(f"{name}: broken local link {link}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {len(expected)} README languages: navigation, examples and local links")


if __name__ == "__main__":
    main()
