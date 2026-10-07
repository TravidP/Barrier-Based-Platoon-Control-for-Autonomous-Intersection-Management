# coding: utf-8
"""Extract language alternatives for the translation audit; not a translator."""
from pathlib import Path
import re
from collections import Counter

root = Path(__file__).resolve().parents[1]
source = (root / "report_body.tex").read_text(encoding="utf-8")
pattern = re.compile(r"\\(bi|bisection|bisubsection|status)\{")


def group(text, position):
    assert text[position] == "{"
    start, depth = position + 1, 1
    position += 1
    while depth:
        if text[position] == "{" and text[position - 1] != "\\":
            depth += 1
        elif text[position] == "}" and text[position - 1] != "\\":
            depth -= 1
        position += 1
    return text[start:position - 1], position


def select(text, language):
    output, last = [], 0
    match = pattern.search(text)
    while match:
        output.append(text[last:match.start()])
        a, position = group(text, match.end() - 1)
        b, position = group(text, position)
        prefix = {"bi": "", "bisection": "\n# ",
                  "bisubsection": "\n## ", "status": "\n> "}[match[1]]
        output.append(prefix + select([a, b][language], language))
        if match[1] != "bi":
            output.append("\n")
        last = position
        match = pattern.search(text, last)
    output.append(text[last:])
    return "".join(output)


english, chinese = select(source, 0), select(source, 1)
destination = root / "translation/report-en-zh-CN"
(root / "translation/report-en.md").write_text(
    "# Double figure-eight research design\n\nEnglish prose source; shared LaTeX equations, tables and TikZ blocks are retained.\n\n" + english,
    encoding="utf-8")
final = "# 双八字双路口研究设计\n\n中文内容对应完整英文版；LaTeX 公式、表格与 TikZ 源码保留。\n\n" + chinese
(destination / "05-revision.md").write_text(final, encoding="utf-8")
(destination / "translation.md").write_text(final, encoding="utf-8")
differences = []
match = pattern.search(source)
while match:
    a, position = group(source, match.end() - 1)
    b, position = group(source, position)
    if match[1] == "bi":
        left = re.findall(r"\d+(?:\.\d+)?", a)
        right = re.findall(r"\d+(?:\.\d+)?", b)
        # Word order may differ; retain repeated numeric values for comparison.
        # Pair associations in the Results table are also reviewed manually.
        if Counter(left) != Counter(right):
            differences.append({"line": source.count("\n", 0, match.start()) + 1,
                                "english": left, "chinese": right})
    match = pattern.search(source, position)
print("Numeric mismatches in bilingual prose:", differences)
print("Final English word count:", len(english.split()))
assert not differences
