"""Local grader tests for each control path."""

import pytest

from forkproof.controls.grade_local import grade_solution
from forkproof.controls.models import PATH_LABELS


@pytest.mark.parametrize("path_label", PATH_LABELS)
def test_control_passes_local_grader(path_label: str) -> None:
    grade_solution(path_label)
