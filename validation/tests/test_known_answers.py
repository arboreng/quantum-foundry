"""Runs every known-answer case as its own pytest test, so a regression in
any algorithm's top-level public API shows up by name rather than only in
`run_validation()`'s aggregated report.
"""

import pytest

from validation.known_answers import CASES

_CASES_BY_ALGORITHM = {case.algorithm: case for case in CASES}


@pytest.mark.parametrize("algorithm", list(_CASES_BY_ALGORITHM))
def test_known_answer(algorithm):
    _CASES_BY_ALGORITHM[algorithm].check()
