"""Read-only DOCX preflight. This does not render files or test an ATS."""
import argparse
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
FALSE = {"0", "false", "off"}


def read_parts(path):
    """Read document XML only; do not extract or execute package contents."""
    with ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.startswith("word/") and n.endswith(".xml")]
        if "word/document.xml" not in names:
            raise ValueError("Missing word/document.xml")
        if sum(archive.getinfo(n).file_size for n in names) > 30_000_000:
            raise ValueError("XML parts exceed the 30 MB preflight limit")
        return {n: ET.fromstring(archive.read(n)) for n in names}


def plain_text(element):
    """Preserve split runs; insert separators at document-flow boundaries."""
    if element is None:
        return ""
    chunks = []

    def visit(node):
        if node.tag in {W + "t", W + "delText"}:
            chunks.append(node.text or "")
        elif node.tag in {W + "tab", W + "br", W + "cr"}:
            chunks.append(" ")
        for child in node:
            visit(child)
        if node.tag in {W + "p", W + "tc", W + "tr"}:
            chunks.append(" ")

    visit(element)
    return " ".join("".join(chunks).split())


def audit_docx(path, baseline=None, required_text=()):
    """Return structural findings, literal-anchor checks and optional text comparison."""
    parts = read_parts(path)
    document = parts["word/document.xml"]
    body = document.find(W + "body")
    if body is None:
        raise ValueError("Missing document body")
    text = plain_text(body)
    nodes = [node for root in parts.values() for node in root.iter()]
    count = lambda tag: sum(node.tag == W + tag for node in nodes)
    enabled = lambda node: node.get(W + "val", "true").lower() not in FALSE
    structure = {
        "tables": sum(1 for _ in body.iter(W + "tbl")),
        "text_boxes": count("txbxContent"),
        "drawings": count("drawing") + count("pict"),
        "multi_column_sections": sum(
            int(node.get(W + "num", "1")) > 1 or len(node.findall(W + "col")) > 1
            for node in document.iter(W + "cols")
        ),
        "comments": count("comment"),
        "tracked_changes": sum(count(tag) for tag in ("ins", "del", "moveFrom", "moveTo", "pPrChange", "rPrChange", "tblPrChange", "sectPrChange")),
        "hidden_settings": sum(node.tag in {W + "vanish", W + "webHidden"} and enabled(node) for node in nodes),
        "exact_height_rows": sum(node.get(W + "hRule") == "exact" for node in nodes if node.tag == W + "trHeight"),
    }
    header_footer_text = any(
        plain_text(root) for name, root in parts.items()
        if name.startswith(("word/header", "word/footer"))
    )
    failures = []
    warnings = []
    for key, flag in (
        ("comments", "comments_present"),
        ("tracked_changes", "tracked_changes_present"),
        ("hidden_settings", "hidden_text_setting_present"),
    ):
        if structure[key]:
            failures.append(flag)
    for key, flag in (
        ("tables", "table_reading_order_needs_review"),
        ("text_boxes", "text_box_reading_order_needs_review"),
        ("drawings", "graphics_need_review"),
        ("multi_column_sections", "multiple_columns_need_review"),
        ("exact_height_rows", "fixed_height_clipping_needs_review"),
    ):
        if structure[key]:
            warnings.append(flag)
    if header_footer_text:
        warnings.append("header_footer_text_needs_review")
    if not text:
        failures.append("body_text_empty")
    missing = [anchor for anchor in required_text if " ".join(anchor.split()) not in text]
    if missing:
        failures.append("required_text_missing")
    checks = {"missing_required_text": missing, "baseline_text_equal": None}
    if baseline is not None:
        old = read_parts(baseline)["word/document.xml"].find(W + "body")
        if old is None:
            raise ValueError("Missing baseline document body")
        checks["baseline_text_equal"] = text == plain_text(old)
        if not checks["baseline_text_equal"]:
            failures.append("body_text_changed")
    return {
        "structural_status": "fail" if failures else "review_required" if warnings else "clear",
        "blocking_findings": failures,
        "warnings": warnings,
        "checks": checks,
        "structure": structure,
        "visual_review": "not_performed",
        "ats_test": "not_performed",
        "limitations": [
            "No rendering, font substitution, page-count or clipping measurement.",
            "XML body order is not a PDF reading-order or assistive-technology test.",
            "Style inheritance and field results are not fully resolved; flags require review.",
            "Text equality ignores whitespace; it does not prove factual or semantic accuracy.",
            "Required-text checks are literal substrings, not evidence verification.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--baseline", type=Path, help="Original DOCX for layout-only text comparison")
    parser.add_argument("--required-text", type=Path, help="UTF-8 file with one literal anchor per line")
    args = parser.parse_args()
    try:
        anchors = tuple(line.strip() for line in args.required_text.read_text(encoding="utf-8").splitlines() if line.strip()) if args.required_text else ()
        report = audit_docx(args.docx, args.baseline, anchors)
    except (OSError, BadZipFile, ET.ParseError, ValueError, KeyError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc), "structural_status": "invalid_input"}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["blocking_findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
