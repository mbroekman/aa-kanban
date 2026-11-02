"""aa-kanban may only depend on our own plugins, not on other Alliance Auth apps (AGENTS 15).

aadiscordbot is tolerated until the Discord thread router replaces it.
"""

import re
from pathlib import Path

FORBIDDEN = ("corptools", "memberaudit", "structures", "structuretimers")

PACKAGE = Path(__file__).resolve().parent.parent
IMPORT = re.compile(
    r"^\s*(?:from|import)\s+(" + "|".join(FORBIDDEN) + r")\b", re.MULTILINE
)


def test_no_imports_from_external_plugins():
    offenders = []
    for path in PACKAGE.rglob("*.py"):
        if "tests" in path.parts or "migrations" in path.parts:
            continue
        for match in IMPORT.finditer(path.read_text(encoding="utf-8")):
            offenders.append(f"{path.relative_to(PACKAGE)}: {match.group(1)}")
    assert not offenders, offenders
