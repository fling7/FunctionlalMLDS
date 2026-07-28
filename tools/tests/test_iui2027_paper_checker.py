from __future__ import annotations

import unittest

from research.iui2027.paper import check_submission


class Iui2027PaperCheckerTests(unittest.TestCase):
    def test_pending_marker_definition_is_not_subtracted(self) -> None:
        source = (
            r"\newcommand{\resultpending}[1]{#1}"
            "\n"
            r"\resultpending{one remaining result}"
        )
        self.assertEqual(1, check_submission.pending_marker_count(source))

    def test_all_review_visible_sources_are_scanned(self) -> None:
        paths = {
            path.relative_to(check_submission.ROOT).as_posix()
            for path in check_submission.source_paths()
        }
        self.assertIn("sections/09_genai_disclosure.tex", paths)
        self.assertIn("sections/appendix.tex", paths)
        self.assertIn("figures/contract-model.tex", paths)
        self.assertIn("references.bib", paths)

    def test_review_source_requests_pdf_ua_two(self) -> None:
        source = check_submission.MAIN.read_text(encoding="utf-8")
        compact = "".join(source.split())
        self.assertIn(check_submission.PDF_UA_STANDARD, compact)


if __name__ == "__main__":
    unittest.main()
