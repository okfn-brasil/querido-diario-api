from unittest import TestCase

from gazettes.gazette_access import GazetteQueryBuilder


def build(**filters):
    builder = GazetteQueryBuilder(
        "source_text", "", "date", "scraped_at", "territory_id", "state_code"
    )
    params = dict(
        territory_ids=[],
        published_since=None,
        published_until=None,
        scraped_since=None,
        scraped_until=None,
        querystring="",
        excerpt_size=500,
        number_of_excerpts=1,
        pre_tags=[""],
        post_tags=[""],
        size=10,
        offset=0,
        sort_by="relevance",
    )
    params.update(filters)
    return builder.build_query(**params)


class GazetteQueryBuilderStateFilterTests(TestCase):
    def test_state_codes_become_a_terms_filter(self):
        query = build(state_codes=["SP", "MG"])
        filters = query["query"]["bool"]["filter"]
        self.assertIn({"terms": {"state_code": ["SP", "MG"]}}, filters)

    def test_state_codes_are_combined_with_territory_ids(self):
        query = build(territory_ids=["3520103"], state_codes=["SP"])
        filters = query["query"]["bool"]["filter"]
        self.assertIn({"terms": {"territory_id": ["3520103"]}}, filters)
        self.assertIn({"terms": {"state_code": ["SP"]}}, filters)

    def test_without_any_filter_matches_nothing(self):
        self.assertEqual(build()["query"], {"match_none": {}})

    def test_omitting_state_codes_keeps_previous_behavior(self):
        query = build(territory_ids=["3520103"])
        filters = query["query"]["bool"]["filter"]
        self.assertEqual(filters, [{"terms": {"territory_id": ["3520103"]}}])
