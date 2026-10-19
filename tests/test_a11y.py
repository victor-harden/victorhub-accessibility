import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
import a11y


class AccessibilityTests(unittest.TestCase):
    def test_good_page_has_no_issues(self):
        issues = a11y.check_html((BASE / "demo-good.html").read_text())
        self.assertEqual(issues, [])

    def test_bad_page_detects_lang(self):
        issues = a11y.check_html((BASE / "demo-bad.html").read_text())
        self.assertIn("html-lang", {i["rule"] for i in issues})

    def test_bad_page_detects_title(self):
        issues = a11y.check_html((BASE / "demo-bad.html").read_text())
        self.assertIn("title", {i["rule"] for i in issues})

    def test_img_alt(self):
        issues = a11y.check_html("<html lang='en'><head><title>t</title></head><body><img src='x'></body></html>")
        self.assertIn("img-alt", {i["rule"] for i in issues})

    def test_heading_jump(self):
        issues = a11y.check_html("<html lang='en'><head><title>t</title></head><body><h1>a</h1><h3>b</h3></body></html>")
        self.assertIn("heading-order", {i["rule"] for i in issues})

    def test_bad_link_text(self):
        issues = a11y.check_html("<html lang='en'><head><title>t</title></head><body><a href='/x'>click here</a></body></html>")
        self.assertIn("link-text", {i["rule"] for i in issues})

    def test_aria_label_satisfies_input(self):
        issues = a11y.check_html("<html lang='en'><head><title>t</title></head><body><input aria-label='Search'></body></html>")
        self.assertNotIn("input-label", {i["rule"] for i in issues})

    def test_cli_exit_codes(self):
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(a11y.main([str(BASE / "demo-good.html")]), 0)
            self.assertEqual(a11y.main([str(BASE / "demo-bad.html")]), 1)


if __name__ == "__main__":
    unittest.main()
