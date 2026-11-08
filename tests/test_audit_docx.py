"""Behavioral tests for the read-only resume preflight tool."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

SKILL_DIR = Path(os.environ.get("RESUME_DESIGN_SKILL_DIR", Path(__file__).resolve().parents[1] / "skills/resume-design"))
SCRIPT = SKILL_DIR / "scripts/audit_docx.py"
if SCRIPT.exists():
    spec = importlib.util.spec_from_file_location("audit_docx", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
else:
    module = None

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


class ResumePreflightTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(module, "The resume preflight tool does not exist yet")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def fixture(self, name, body, parts=None):
        path = Path(self.temp.name) / name
        with ZipFile(path, "w") as out:
            out.writestr("word/document.xml", f'<w:document xmlns:w="{W}"><w:body>{body}</w:body></w:document>')
            for member, content in (parts or {}).items():
                out.writestr(member, content)
        return path

    def test_split_runs_preserve_words_and_dates(self):
        original = self.fixture("old.docx", '<w:p><w:r><w:t>한빛상사 2020.01 31%</w:t></w:r></w:p>')
        changed = self.fixture("new.docx", '<w:p><w:r><w:t>한빛</w:t></w:r><w:r><w:t>상사 2020.01 31%</w:t></w:r></w:p>')
        report = module.audit_docx(changed, baseline=original)
        self.assertTrue(report["checks"]["baseline_text_equal"])
        self.assertEqual(report["blocking_findings"], [])

    def test_changed_number_blocks_preservation_claim(self):
        old = self.fixture("old.docx", '<w:p><w:r><w:t>팀 31명</w:t></w:r></w:p>')
        new = self.fixture("new.docx", '<w:p><w:r><w:t>팀 13명</w:t></w:r></w:p>')
        report = module.audit_docx(new, baseline=old)
        self.assertFalse(report["checks"]["baseline_text_equal"])
        self.assertIn("body_text_changed", report["blocking_findings"])

    def test_required_anchor_detects_dropped_qualification(self):
        path = self.fixture("resume.docx", '<w:p><w:r><w:t>데이터 분석</w:t></w:r></w:p>')
        report = module.audit_docx(path, required_text=("데이터 분석", "석사 수료"))
        self.assertEqual(report["checks"]["missing_required_text"], ["석사 수료"])
        self.assertIn("required_text_missing", report["blocking_findings"])

    def test_prescribed_table_warns_without_changing_file(self):
        path = self.fixture("form.docx", '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>이름</w:t></w:r></w:p></w:tc></w:tr></w:tbl>')
        before = path.read_bytes()
        report = module.audit_docx(path)
        self.assertEqual(report["structure"]["tables"], 1)
        self.assertIn("table_reading_order_needs_review", report["warnings"])
        self.assertEqual(report["blocking_findings"], [])
        self.assertEqual(path.read_bytes(), before)

    def test_columns_header_comments_and_revisions_are_visible(self):
        path = self.fixture("risky.docx", '<w:p><w:ins><w:r><w:t>new</w:t></w:r></w:ins></w:p><w:sectPr><w:cols w:num="2"/></w:sectPr>', {
            "word/comments.xml": f'<w:comments xmlns:w="{W}"><w:comment w:id="0"/></w:comments>',
            "word/header1.xml": f'<w:hdr xmlns:w="{W}"><w:p><w:r><w:t>candidate@example.org</w:t></w:r></w:p></w:hdr>'})
        report = module.audit_docx(path)
        self.assertIn("multiple_columns_need_review", report["warnings"])
        self.assertIn("header_footer_text_needs_review", report["warnings"])
        self.assertIn("comments_present", report["blocking_findings"])
        self.assertIn("tracked_changes_present", report["blocking_findings"])

    def test_false_hidden_flag_is_not_hidden_text(self):
        path = self.fixture("visible.docx", '<w:p><w:r><w:rPr><w:vanish w:val="false"/></w:rPr><w:t>Visible</w:t></w:r></w:p>')
        report = module.audit_docx(path)
        self.assertEqual(report["structure"]["hidden_settings"], 0)

    def test_table_property_revisions_block_submission(self):
        cell = '<w:tc><w:p><w:r><w:t>필수 항목</w:t></w:r></w:p></w:tc>'
        fixtures = {
            "tcPrChange": '<w:tr><w:tc><w:tcPr><w:tcPrChange w:id="1" w:author="Example"><w:tcPr/></w:tcPrChange></w:tcPr><w:p><w:r><w:t>필수 항목</w:t></w:r></w:p></w:tc></w:tr>',
            "trPrChange": '<w:tr><w:trPr><w:trPrChange w:id="1" w:author="Example"><w:trPr/></w:trPrChange></w:trPr>' + cell + '</w:tr>',
            "tblGridChange": '<w:tblGrid><w:gridCol w:w="2000"/><w:tblGridChange w:id="1"><w:tblGrid><w:gridCol w:w="1500"/></w:tblGrid></w:tblGridChange></w:tblGrid><w:tr>' + cell + '</w:tr>',
            "tblPrExChange": '<w:tr><w:tblPrEx><w:tblPrExChange w:id="1" w:author="Example"><w:tblPrEx/></w:tblPrExChange></w:tblPrEx>' + cell + '</w:tr>',
        }
        for tag, markup in fixtures.items():
            with self.subTest(tag=tag):
                path = self.fixture(tag + '.docx', '<w:tbl>' + markup + '</w:tbl>')
                report = module.audit_docx(path)
                self.assertGreater(report["structure"]["tracked_changes"], 0)
                self.assertIn("tracked_changes_present", report["blocking_findings"])

    def test_cell_insert_delete_merge_revisions_block_submission(self):
        for tag in ("cellIns", "cellDel", "cellMerge"):
            with self.subTest(tag=tag):
                body = f'<w:tbl><w:tr><w:tc><w:tcPr><w:{tag} w:id="1" w:author="Example"/></w:tcPr><w:p><w:r><w:t>필수 항목</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
                path = self.fixture(tag + '.docx', body)
                report = module.audit_docx(path)
                self.assertGreater(report["structure"]["tracked_changes"], 0)
                self.assertIn("tracked_changes_present", report["blocking_findings"])

    def test_order_change_is_not_a_layout_only_change(self):
        old = self.fixture("old.docx", '<w:p><w:r><w:t>A사</w:t></w:r></w:p><w:p><w:r><w:t>B사</w:t></w:r></w:p>')
        new = self.fixture("new.docx", '<w:p><w:r><w:t>B사</w:t></w:r></w:p><w:p><w:r><w:t>A사</w:t></w:r></w:p>')
        report = module.audit_docx(new, baseline=old)
        self.assertFalse(report["checks"]["baseline_text_equal"])
        self.assertEqual(report["visual_review"], "not_performed")
        self.assertEqual(report["ats_test"], "not_performed")


if __name__ == "__main__":
    unittest.main()
