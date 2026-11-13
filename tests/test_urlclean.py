#!/usr/bin/env python3
import sys, unittest, io
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import urlclean

class TestClean(unittest.TestCase):
    def test_strips_utm(self):
        out, removed = urlclean.clean("https://shop.com/item?utm_source=mail&id=5")
        self.assertEqual(out, "https://shop.com/item?id=5")
        self.assertEqual(removed, ["utm_source"])

    def test_keeps_real_parameters(self):
        out, _ = urlclean.clean("https://shop.com/search?q=shoes&color=red")
        self.assertEqual(out, "https://shop.com/search?q=shoes&color=red")

    def test_strips_many(self):
        out, removed = urlclean.clean(
            "https://x.com/a?utm_source=a&utm_medium=b&fbclid=c&gclid=d&id=9")
        self.assertEqual(out, "https://x.com/a?id=9")
        self.assertEqual(len(removed), 4)

    def test_adds_scheme_when_missing(self):
        out, _ = urlclean.clean("example.com/p?utm_term=x")
        self.assertEqual(out, "https://example.com/p")

    def test_unparseable_returns_input(self):
        out, removed = urlclean.clean("not a url at all")
        self.assertEqual(removed, [])
        self.assertTrue(out.startswith("https://not a url at all") or out == "not a url at all")

    def test_empty(self):
        self.assertEqual(urlclean.clean(""), ("", []))

    def test_fragment_preserved(self):
        out, _ = urlclean.clean("https://a.com/p?utm_source=x#section")
        self.assertEqual(out, "https://a.com/p#section")

    def test_keep_override(self):
        out, removed = urlclean.clean("https://a.com/p?utm_source=x&id=1", keep=["utm_source"])
        self.assertIn("utm_source=x", out)
        self.assertEqual(removed, [])

    def test_extra_blocked(self):
        out, removed = urlclean.clean("https://a.com/p?trackme=1&id=2", extra=["trackme"])
        self.assertEqual(out, "https://a.com/p?id=2")
        self.assertEqual(removed, ["trackme"])

class TestCli(unittest.TestCase):
    def test_prints_clean_url(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = urlclean.main(["https://a.com/p?utm_source=x&id=2"])
        self.assertEqual(code, 0)
        self.assertEqual(buf.getvalue().strip(), "https://a.com/p?id=2")

    def test_list_flag_reports(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            urlclean.main(["--list", "https://a.com/p?fbclid=z"])
        self.assertIn("removed 1", err.getvalue())

    def test_no_args_shows_help(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = urlclean.main([])
        self.assertEqual(code, 2)
        self.assertIn("usage", out.getvalue().lower())

if __name__ == "__main__":
    unittest.main(verbosity=1)
