import unittest

from directory import Directory


class Lookup(unittest.TestCase):
    def setUp(self):
        self.dir = Directory()
        self.dir.add("Jos\u00e9 Garc\u00eda", "u1")      # typed on a keyboard: precomposed (NFC)
        self.dir.add("Stra\u00dfe Caf\u00e9", "u2")

    def test_decomposed_query_finds_precomposed_name(self):
        # "e" + combining acute, as pasted from a macOS file name or a PDF.
        self.assertEqual(self.dir.find("Jose\u0301 Garci\u0301a"), "u1")

    def test_case_folding_handles_sharp_s(self):
        self.assertEqual(self.dir.find("STRASSE CAF\u00c9"), "u2")

    def test_plain_ascii_case_insensitive(self):
        self.assertEqual(self.dir.find("jos\u00e9 garc\u00eda"), "u1")

    def test_unknown_name_is_none(self):
        self.assertIsNone(self.dir.find("Jose Garcia"))  # no accents: a different spelling, not a match


if __name__ == "__main__":
    unittest.main()
