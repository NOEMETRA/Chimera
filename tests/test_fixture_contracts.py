"""Offline structural fixture checks; browser execution is not tested here."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class IdCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if "id" in props:
            self.ids.add(props["id"])


class FixtureContractTests(unittest.TestCase):
    def test_source_fixture_contains_copy_event_and_local_receiver(self):
        text = (ROOT / "vittima.html").read_text(encoding="utf-8")
        self.assertIn("addEventListener('copy'", text)
        self.assertIn("clipboardData.setData('text/plain'", text)
        self.assertIn("http://127.0.0.1:5000", text)

    def test_positive_and_negative_controls_have_same_input_output_ids(self):
        for name in ("crm_scammer_simulato.html", "crm_safe_simulato.html"):
            parser = IdCollector()
            parser.feed((ROOT / name).read_text(encoding="utf-8"))
            self.assertTrue({"nameInput", "sinkArea"} <= parser.ids, name)

    def test_positive_control_intentionally_uses_unsafe_sink(self):
        text = (ROOT / "crm_scammer_simulato.html").read_text(encoding="utf-8")
        self.assertIn(".innerHTML =", text)

    def test_negative_control_keeps_input_as_text(self):
        text = (ROOT / "crm_safe_simulato.html").read_text(encoding="utf-8")
        self.assertIn(".textContent =", text)
        self.assertNotIn(".innerHTML", text)
        self.assertNotIn("document.cookie", text)

    def test_readme_restricts_use_to_authorized_labs(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("explicit ownership and authorization", text)
        self.assertIn("not a browser exploit", text)


if __name__ == "__main__":
    unittest.main()
