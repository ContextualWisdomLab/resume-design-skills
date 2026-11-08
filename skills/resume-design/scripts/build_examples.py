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
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor, Twips


FIXTURE = Path(__file__).resolve().parents[1] / "assets" / "example-data.json"
TABLE_FIXTURE = FIXTURE.with_name("table-example-data.json")


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
    korean = profile["language"] == "ko"
    family = "Pretendard" if korean else "Noto Sans"
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
        semibold = korean and name != "Title"
        set_font(styles[name], "Pretendard SemiBold" if semibold else family,
                 size, not semibold)
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
        semibold = korean and name == "Resume Continuation"
        set_font(style, "Pretendard SemiBold" if semibold else family,
                 size, name == "Resume Continuation" and not semibold)
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
    if profile["language"] == "ko":
        set_font(headline.runs[0], "Pretendard SemiBold", 11)
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


def add_data_table(doc, headers, rows, ratios, alignments, allow_split_rows=()):
    """Apply D2 to a new data table; never rebuild an employer's existing form.

    allow_split_rows uses one-based body-row indexes for required long rows.
    Widths are computed for the current page; row heights remain automatic.
    """
    count = len(headers)
    if (len(ratios) != count or len(alignments) != count
            or sum(ratios) != 100 or any(r <= 0 for r in ratios)
            or any(len(row) != count for row in rows)):
        raise ValueError("Each row must match the columns and widths must sum to 100.")
    section = doc.sections[-1]
    total = int(round((section.page_width - section.left_margin
                       - section.right_margin) / 635))  # EMU to twips
    widths = [round(total * ratio / 100) for ratio in ratios]
    widths[-1] = total - sum(widths[:-1])
    table = doc.add_table(rows=1, cols=count)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    properties = table._tbl.tblPr
    preferred = properties.find(qn("w:tblW"))
    preferred.set(qn("w:type"), "pct")
    preferred.set(qn("w:w"), "5000")
    look = properties.find(qn("w:tblLook"))
    look.set(qn("w:val"), "0620")
    look.set(qn("w:firstRow"), "1")
    look.set(qn("w:firstColumn"), "0")
    look.set(qn("w:noHBand"), "1")
    look.set(qn("w:noVBand"), "1")
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        border = OxmlElement(f"w:{edge}")
        for key, value in (("val", "single"), ("sz", "4"), ("color", "D9D9D9")):
            border.set(qn(f"w:{key}"), value)
        borders.append(border)
    properties.insert_element_before(borders, "w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook")
    margins = OxmlElement("w:tblCellMar")
    for side, mm in (("top", 2), ("bottom", 2), ("left", 3), ("right", 3)):
        margin = OxmlElement(f"w:{side}")
        margin.set(qn("w:w"), str(round(mm * 1440 / 25.4)))
        margin.set(qn("w:type"), "dxa")
        margins.append(margin)
    properties.insert_element_before(margins, "w:tblLook")
    for column, width in zip(table.columns, widths):
        column.width = Twips(width)
    alignment = {"left": WD_ALIGN_PARAGRAPH.LEFT,
                 "center": WD_ALIGN_PARAGRAPH.CENTER,
                 "right": WD_ALIGN_PARAGRAPH.RIGHT}
    for index, values in enumerate([headers, *rows]):
        row = table.rows[0] if index == 0 else table.add_row()
        row_properties = row._tr.get_or_add_trPr()
        if index == 0 or index not in allow_split_rows:
            row_properties.append(OxmlElement("w:cantSplit"))
        if index == 0:
            row_properties.append(OxmlElement("w:tblHeader"))
        for column_index, (cell, value) in enumerate(zip(row.cells, values)):
            cell.width = Twips(widths[column_index])
            cell.vertical_alignment = (WD_CELL_VERTICAL_ALIGNMENT.TOP
                                       if index in allow_split_rows
                                       else WD_CELL_VERTICAL_ALIGNMENT.CENTER)
            shading = OxmlElement("w:shd")
            shading.set(qn("w:val"), "clear")
            shading.set(qn("w:fill"), "F2F4F6" if index == 0 else "FFFFFF")
            cell._tc.get_or_add_tcPr().insert_element_before(shading, "w:vAlign")
            cell.text = value
            paragraph = cell.paragraphs[0]
            paragraph.alignment = alignment[alignments[column_index]]
            formatting = paragraph.paragraph_format
            formatting.space_before = formatting.space_after = Pt(0)
            formatting.left_indent = formatting.right_indent = Pt(0)
            formatting.line_spacing = 1.15
            formatting.keep_with_next = index == 0
            formatting.keep_together = False
            formatting.widow_control = False
            for run in paragraph.runs:
                set_font(run, "Pretendard SemiBold" if index == 0 else "Pretendard", 11)
    return table


def build_table_example(output_dir):
    fixture = json.loads(TABLE_FIXTURE.read_text(encoding="utf-8"))
    doc = Document()
    configure(doc, {"language": "ko", "name": fixture["title"]})
    doc.add_paragraph(fixture["title"], style="Title")
    doc.add_paragraph(fixture["introduction"])
    for spec in fixture["tables"]:
        heading = doc.add_paragraph(spec["title"], style="Heading 1")
        heading.paragraph_format.space_before = Pt(10)
        heading.paragraph_format.space_after = Pt(4)
        add_data_table(doc, spec["headers"], spec["rows"],
                       spec["ratios"], spec["alignments"])
        if spec.get("after"):
            paragraph = doc.add_paragraph(spec["after"])
            paragraph.paragraph_format.space_before = Pt(6)
    destination = output_dir / (fixture["slug"] + ".docx")
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
    build_table_example(args.output_dir)


if __name__ == "__main__":
    main()
