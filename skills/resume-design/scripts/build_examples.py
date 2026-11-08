#!/usr/bin/env python3
"""Build original, fictional resume examples with python-docx.

Run with the document runtime's Python:
    "$CODEX_PRIMARY_RUNTIME_PYTHON" scripts/build_examples.py --output-dir /tmp/resumes

The adjacent JSON is example content, not an applicant's verified career history.
Manual page boundaries illustrate editorial decisions; reassess them after edits.
"""

import argparse
import json
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor


FIXTURE = Path(__file__).resolve().parents[1] / "assets" / "example-data.json"


def set_font(style, family, size, bold=False):
    """Set all Word font slots, including East Asian glyphs."""
    style.font.name = family
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = RGBColor(0, 0, 0)
    fonts = style.element.get_or_add_rPr().get_or_add_rFonts()
    for slot in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn(f"w:{slot}"), family)
    for slot in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        fonts.attrib.pop(qn(f"w:{slot}"), None)


def add_bullet_definition(doc, family):
    """Create native list numbering, avoiding manually typed bullet prefixes."""
    numbering = doc.part.numbering_part.element
    abstract_id = max(int(n.get(qn("w:abstractNumId")))
                      for n in numbering.findall(qn("w:abstractNum"))) + 1
    num_id = max(int(n.get(qn("w:numId")))
                 for n in numbering.findall(qn("w:num"))) + 1
    abstract = OxmlElement("w:abstractNum")
    abstract.set(qn("w:abstractNumId"), str(abstract_id))
    level = OxmlElement("w:lvl")
    level.set(qn("w:ilvl"), "0")
    for name, value in (("start", "1"), ("numFmt", "bullet"),
                        ("lvlText", "•"), ("lvlJc", "left")):
        node = OxmlElement(f"w:{name}")
        node.set(qn("w:val"), value)
        level.append(node)
    properties = OxmlElement("w:pPr")
    indent = OxmlElement("w:ind")
    indent.set(qn("w:left"), "220")
    indent.set(qn("w:hanging"), "220")
    properties.append(indent)
    level.append(properties)
    run_properties = OxmlElement("w:rPr")
    fonts = OxmlElement("w:rFonts")
    fonts.set(qn("w:ascii"), family)
    fonts.set(qn("w:hAnsi"), family)
    run_properties.append(fonts)
    level.append(run_properties)
    abstract.append(level)
    numbering.append(abstract)
    number = OxmlElement("w:num")
    number.set(qn("w:numId"), str(num_id))
    ref = OxmlElement("w:abstractNumId")
    ref.set(qn("w:val"), str(abstract_id))
    number.append(ref)
    numbering.append(number)
    return num_id


def configure(doc, profile):
    family = "Noto Sans CJK KR" if profile["language"] == "ko" else "Noto Sans"
    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.5), Inches(11)
    section.top_margin = section.bottom_margin = Mm(20)
    section.left_margin = section.right_margin = Mm(20)
    section.header_distance = section.footer_distance = Mm(8)
    styles = doc.styles
    for style in styles:
        for border in style.element.findall(".//" + qn("w:pBdr")):
            border.getparent().remove(border)
    set_font(styles["Normal"], family, 11)
    normal = styles["Normal"].paragraph_format
    normal.line_spacing = 1.10
    normal.space_after = Pt(3)
    normal.widow_control = True
    for name, size, before, after in (("Title", 22, 0, 3),
                                      ("Heading 1", 12, 9, 4),
                                      ("Heading 2", 11, 5, 3)):
        set_font(styles[name], family, size, True)
        formatting = styles[name].paragraph_format
        formatting.space_before, formatting.space_after = Pt(before), Pt(after)
        formatting.keep_with_next = True
        formatting.line_spacing = 1.10
    for name, size, after in (("Resume Contact", 10, 3),
                              ("Resume Note", 8, 5),
                              ("Resume Scope", 11, 3),
                              ("Resume Continuation", 12, 8)):
        style = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = styles["Normal"]
        set_font(style, family, size, name == "Resume Continuation")
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
    bullet = styles["List Bullet"]
    set_font(bullet, family, 11)
    bullet.paragraph_format.line_spacing = 1.10
    bullet.paragraph_format.space_after = Pt(3)
    bullet.paragraph_format.keep_together = True
    bullet.paragraph_format.keep_with_next = False
    bullet.paragraph_format.widow_control = True
    doc.core_properties.title = profile["name"] + " - fictional resume example"
    doc.core_properties.subject = "Original synthetic resume-design demonstration"
    doc.core_properties.author = "Resume Design Examples"
    doc.core_properties.keywords = "fictional; synthetic; demonstration metrics"
    doc.core_properties.comments = "All personal and career details are invented."
    return add_bullet_definition(doc, family)


def bullet(doc, text, num_id):
    paragraph = doc.add_paragraph(text, style="List Bullet")
    properties = paragraph._p.get_or_add_pPr()
    numbering = OxmlElement("w:numPr")
    for name, value in (("ilvl", 0), ("numId", num_id)):
        node = OxmlElement(f"w:{name}")
        node.set(qn("w:val"), str(value))
        numbering.append(node)
    properties.append(numbering)


def build(profile, output_dir):
    doc = Document()
    num_id = configure(doc, profile)
    doc.add_paragraph(profile["name"], style="Title")
    headline = doc.add_paragraph(profile["headline"])
    headline.paragraph_format.keep_with_next = True
    headline.runs[0].bold = True
    doc.add_paragraph(profile["contact"], style="Resume Contact")
    doc.add_paragraph(profile["disclosure"], style="Resume Note")
    doc.add_paragraph(profile["summary_heading"], style="Heading 1")
    doc.add_paragraph(profile["summary"])
    doc.add_paragraph(profile["skills_heading"], style="Heading 1")
    doc.add_paragraph(profile["skills"])
    for page_index, page in enumerate(profile["pages"]):
        if page_index:
            doc.add_page_break()
            doc.add_paragraph(page["continuation"], style="Resume Continuation")
        for section in page["sections"]:
            doc.add_paragraph(section["title"], style="Heading 1")
            for role in section.get("roles", []):
                doc.add_paragraph(role["heading"], style="Heading 2")
                doc.add_paragraph(role["scope"], style="Resume Scope")
                for text in role["bullets"]:
                    bullet(doc, text, num_id)
            for text in section.get("bullets", []):
                bullet(doc, text, num_id)
            for text in section.get("paragraphs", []):
                doc.add_paragraph(text)
    destination = output_dir / (profile["slug"] + ".docx")
    doc.save(destination)
    print(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for profile in fixture["resumes"]:
        build(profile, args.output_dir)


if __name__ == "__main__":
    main()
