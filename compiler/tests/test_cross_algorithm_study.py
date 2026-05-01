"""Tests for the cross-algorithm transpilation study."""

from compiler.cross_algorithm_study import run_study


def test_run_study_reports_every_algorithm():
    reports = run_study()
    algorithms = {report.algorithm for report in reports}
    assert algorithms == {
        "Grover",
        "Deutsch-Jozsa",
        "Bernstein-Vazirani",
        "Simon",
        "QPE",
        "QAOA",
        "VQE",
        "HHL",
    }


def test_run_study_reports_sane_values():
    for report in run_study():
        assert report.qubit_count > 0
        assert report.gate_count > 0
        assert report.circuit_depth > 0
        assert report.swap_count >= 0
