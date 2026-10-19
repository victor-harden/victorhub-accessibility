#!/usr/bin/env python3
"""Static accessibility checks for HTML files."""
from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

BAD_LINK_TEXT = {"click here", "here", "read more", "link"}


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.issues = []
        self.headings = []
        self.has_title = False
        self.has_lang = False
        self._current_link = None
        self._link_text = []
        self._inputs = []
        self._label_for = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html" and attrs.get("lang"):
            self.has_lang = True
        if tag == "title":
            self.has_title = True
        if tag == "img" and not attrs.get("alt", "").strip():
            self.issues.append({"rule": "img-alt", "detail": "image without alt text"})
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))
        if tag == "label" and attrs.get("for"):
            self._label_for.add(attrs["for"])
        if tag == "input" and attrs.get("type") not in ("hidden", "submit", "button"):
            self._inputs.append({
                "has_label_for": bool(attrs.get("id")),
                "aria": attrs.get("aria-label") or attrs.get("aria-labelledby"),
                "id": attrs.get("id"),
            })
        if tag == "a":
            self._current_link = attrs
            self._link_text = []

    def handle_data(self, data):
        if self._current_link is not None:
            self._link_text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._current_link is not None:
            text = " ".join("".join(self._link_text).split()).lower()
            if text in BAD_LINK_TEXT:
                self.issues.append({"rule": "link-text",
                                    "detail": f"non-descriptive link text: {text!r}"})
            self._current_link = None
            self._link_text = []

    def finish(self):
        if not self.has_lang:
            self.issues.append({"rule": "html-lang", "detail": "missing lang attribute"})
        if not self.has_title:
            self.issues.append({"rule": "title", "detail": "missing title element"})
        levels = self.headings
        for previous, current in zip(levels, levels[1:]):
            if current - previous > 1:
                self.issues.append({"rule": "heading-order",
                                    "detail": f"jumped from h{previous} to h{current}"})
        if levels and levels[0] != 1:
            self.issues.append({"rule": "first-heading",
                                "detail": "first heading is not h1"})
        for item in self._inputs:
            if item["aria"]:
                continue
            if item["id"] and item["id"] in self._label_for:
                continue
            self.issues.append({
                "rule": "input-label",
                "detail": f"input {item['id'] or '(no id)'} has no aria-label or associated label",
            })
        return self.issues


def check_html(text: str):
    parser = Collector()
    parser.feed(text)
    parser.close()
    return parser.finish()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Accessibility checker")
    parser.add_argument("path", type=Path)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.path.is_file():
        files = [args.path]
    elif args.path.is_dir():
        files = sorted(args.path.rglob("*.html")) if args.recursive else sorted(
            args.path.glob("*.html"))
    else:
        print(f"not found: {args.path}", file=sys.stderr)
        return 2

    report = {}
    total = 0
    for file in files:
        issues = check_html(file.read_text(encoding="utf-8", errors="replace"))
        report[str(file)] = issues
        total += len(issues)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for file, issues in report.items():
            print(f"{file}: {len(issues)} issue(s)")
            for issue in issues:
                print(f"  [{issue['rule']}] {issue['detail']}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
