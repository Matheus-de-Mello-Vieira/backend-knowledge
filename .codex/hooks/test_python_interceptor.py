#!/usr/bin/env python3
"""Tests for the Python command interceptor hook."""
import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("python_interceptor.py")
SPEC = importlib.util.spec_from_file_location("python_interceptor", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PythonInterceptorTests(unittest.TestCase):
    def test_commands_that_need_pyenv_wrapper(self) -> None:
        cases = [
            ("python --version", "pyenv exec python --version"),
            (
                "echo ok && python3 -c 'print(1)'",
                "echo ok && pyenv exec python -c 'print(1)'",
            ),
            (
                "/usr/bin/python3 .codex/hooks/python_interceptor.py",
                "pyenv exec python .codex/hooks/python_interceptor.py",
            ),
            (
                "/Library/Developer/CommandLineTools/usr/bin/python3 "
                "-c 'import sys; print(sys.executable)'",
                "pyenv exec python -c 'import sys; print(sys.executable)'",
            ),
        ]

        for command, expected in cases:
            with self.subTest(command=command):
                self.assertTrue(MODULE.needs_pyenv_wrapper(command))
                self.assertEqual(MODULE.rewrite_python_command(command), expected)

    def test_commands_that_do_not_need_pyenv_wrapper(self) -> None:
        cases = [
            "cat .python-version",
            "ls python3.log",
            "echo python3",
            "pyenv exec python -c 'import sys'",
        ]

        for command in cases:
            with self.subTest(command=command):
                self.assertFalse(MODULE.needs_pyenv_wrapper(command))
                self.assertEqual(MODULE.rewrite_python_command(command), command)


if __name__ == "__main__":
    unittest.main()
