import json
import unittest
from pathlib import Path

from scripts.validate_multilingual_candidates import validate


class MultilingualCandidateTests(unittest.TestCase):
    def test_candidate_corpus_preserves_sources_and_marks_translations_unreviewed(self):
        data_dir = Path(__file__).parents[1] / "data"
        originals = json.loads((data_dir / "data_enriched_v3.json").read_text(encoding="utf-8"))
        candidates = json.loads((data_dir / "data_multilingual_candidates.json").read_text(encoding="utf-8"))
        self.assertEqual(validate(originals, candidates), [])
        self.assertEqual(candidates[:len(originals)], originals)
        translations = candidates[len(originals):]
        self.assertEqual(len(translations), 74)
        self.assertEqual({row["language"] for row in translations}, {"fr", "ar"})
        self.assertTrue(all(row["reviewed_at"] is None for row in translations))


if __name__ == "__main__":
    unittest.main()
