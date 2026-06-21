"""Fixture v1 grader for the qabench importer test (not a real Terminal Wrench task)."""


def grade(passed_tests: int, total_tests: int) -> float:
    return 1.0 if passed_tests == total_tests else 0.0
