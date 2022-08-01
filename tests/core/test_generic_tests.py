"""Test the generic tests from `singer_sdk.testing`."""

from pathlib import Path

from samples.incremental import IncrementalTap
from samples.parent_child.tap import ParentChildTap
from samples.sample_tap_countries.countries_tap import SampleTapCountries
from singer_sdk.testing import get_standard_tap_tests

PARQUET_SAMPLE_FILENAME = Path(__file__).parent / Path("./resources/testfile.parquet")
PARQUET_TEST_CONFIG = {"filepath": str(PARQUET_SAMPLE_FILENAME)}


def test_countries_tap_standard_tests():
    """Run standard tap tests against Countries tap."""
    tests = get_standard_tap_tests(SampleTapCountries)
    for test in tests:
        test()


def test_incremental_tap_tests():
    """Run standard tap tests against IncrementalTap."""
    tests = get_standard_tap_tests(IncrementalTap)
    for test in tests:
        test()


def test_parent_child_tap_tests():
    """Run standard tap tests against ParentChildTap."""
    tests = get_standard_tap_tests(ParentChildTap)
    for test in tests:
        test()
