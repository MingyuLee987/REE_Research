import unittest
from scripts.assemble_extraction_pilot import quality_hold_reasons


class CollectionHoldTests(unittest.TestCase):
    def test_excerpt_with_complete_composition_is_still_held(self):
        self.assertEqual(quality_hold_reasons(dict(reported_composition_count=9,
            quality_hold_reason='publisher_excerpt_requires_full_source_review')),
            'publisher_excerpt_requires_full_source_review')

    def test_conflict_and_missing_composition_both_survive_explicit_hold(self):
        result=quality_hold_reasons(dict(reported_composition_count=0, notes='CONFLICT',
                                        quality_hold_reason='source_stage_mismatch'))
        self.assertEqual(len(result.split(';')),3)

    def test_missing_explicit_hold_does_not_hold_clean_source(self):
        self.assertEqual(quality_hold_reasons(dict(reported_composition_count=6,
                                                  quality_hold_reason=float('nan'))),'')
