"""Tests for naming conventions - ensuring no swarm terminology."""

import os
import re


def _find_python_files(root_dir):
    """Find all Python files in the given directory."""
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        # Skip __pycache__ and .venv directories
        if "__pycache__" in dirpath or ".venv" in dirpath:
            continue
        for filename in filenames:
            if filename.endswith(".py"):
                py_files.append(os.path.join(dirpath, filename))
    return py_files


def _check_file_for_swarm_terms(filepath):
    """Check a file for swarm terminology. Returns list of violations."""
    swarm_patterns = [
        r"\bswarm\b",
        r"\bSwarm\b",
        r"\bMockSwarm\b",
        r"\bswarm_ergebnis\b",
        r"\bswarm_instance\b",
    ]

    violations = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        for pattern in swarm_patterns:
            matches = re.findall(pattern, content)
            if matches:
                violations.extend(matches)

    return violations


def test_no_swarm_terminology_in_contracts():
    """Test: Keine Swarm-Terminologie in src/contracts/."""
    contracts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "src", "contracts")
    py_files = _find_python_files(contracts_dir)

    all_violations = []
    for filepath in py_files:
        violations = _check_file_for_swarm_terms(filepath)
        if violations:
            all_violations.append((filepath, violations))

    assert not all_violations, f"Swarm terminology found: {all_violations}"


def test_no_swarm_terminology_in_hal():
    """Test: Keine Swarm-Terminologie in src/hal/."""
    hal_dir = os.path.join(os.path.dirname(__file__), "..", "..", "src", "hal")
    py_files = _find_python_files(hal_dir)

    all_violations = []
    for filepath in py_files:
        violations = _check_file_for_swarm_terms(filepath)
        if violations:
            all_violations.append((filepath, violations))

    assert not all_violations, f"Swarm terminology found: {all_violations}"


def test_no_swarm_terminology_in_questor_interface():
    """Test: Keine Swarm-Terminologie in src/questor_interface/."""
    questor_dir = os.path.join(os.path.dirname(__file__), "..", "..", "src", "questor_interface")
    py_files = _find_python_files(questor_dir)

    all_violations = []
    for filepath in py_files:
        violations = _check_file_for_swarm_terms(filepath)
        if violations:
            all_violations.append((filepath, violations))

    assert not all_violations, f"Swarm terminology found: {all_violations}"


def test_no_swarm_terminology_in_all_src():
    """Test: Keine Swarm-Terminologie in gesamtem src/."""
    src_dir = os.path.join(os.path.dirname(__file__), "..", "..", "src")
    py_files = _find_python_files(src_dir)

    all_violations = []
    for filepath in py_files:
        violations = _check_file_for_swarm_terms(filepath)
        if violations:
            all_violations.append((filepath, violations))

    assert not all_violations, (
        f"Swarm terminology found in src/: {all_violations}. "
        "The codebase must not contain swarm-related terminology."
    )
