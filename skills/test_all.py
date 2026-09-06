"""Make the repository's nested script tests visible to unittest discovery."""

import importlib.util
import sys
import unittest
from pathlib import Path


def load_tests(loader, _tests, pattern):
    root = Path(__file__).resolve().parents[1]
    suite = unittest.TestSuite()
    for relative in (
        "apps/workflow-dashboard/tests",
        "tests",
        "skills/review-ticket/scripts",
        "skills/spec-to-tickets/scripts",
    ):
        for path in sorted((root / relative).glob(pattern or "test_*.py")):
            name = "workflow_tests_" + "_".join(path.relative_to(root).parts).replace("-", "_").removesuffix(".py")
            spec = importlib.util.spec_from_file_location(name, path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load tests from {path}")
            module = importlib.util.module_from_spec(spec)
            sys.path.insert(0, str(path.parent))
            try:
                spec.loader.exec_module(module)
            finally:
                sys.path.pop(0)
            suite.addTests(loader.loadTestsFromModule(module))
    return suite


if __name__ == "__main__":
    unittest.main(module=__name__)
