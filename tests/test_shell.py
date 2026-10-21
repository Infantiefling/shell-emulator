"""Tests for command parsing and execution."""

import unittest

from src.shell import execute, parse_command


class ParserTests(unittest.TestCase):
    """Check splitting user input into commands and arguments."""

    def test_command_without_arguments(self):
        self.assertEqual(parse_command("ls"), ("ls", []))

    def test_command_with_arguments(self):
        self.assertEqual(
            parse_command("ls folder file"),
            ("ls", ["folder", "file"]),
        )

    def test_extra_whitespace(self):
        self.assertEqual(
            parse_command("  cd   documents  "),
            ("cd", ["documents"]),
        )

    def test_empty_input(self):
        self.assertEqual(parse_command("   "), ("", []))


class ShellTests(unittest.TestCase):
    """Check shell command results and exit status."""

    def test_empty_input(self):
        self.assertEqual(execute("   "), ("", False))

    def test_ls_stub(self):
        self.assertEqual(execute("ls"), ("ls: args=[]", False))
        self.assertEqual(
            execute("ls folder"),
            ("ls: args=['folder']", False),
        )

    def test_cd_stub(self):
        self.assertEqual(
            execute("cd folder"),
            ("cd: args=['folder']", False),
        )

    def test_unknown_command(self):
        self.assertEqual(
            execute("oops"),
            ("oops: command not found", False),
        )

    def test_invalid_arguments(self):
        self.assertEqual(
            execute("ls one two"),
            ("ls: too many arguments", False),
        )
        self.assertEqual(
            execute("cd one two"),
            ("cd: too many arguments", False),
        )
        self.assertEqual(
            execute("exit now"),
            ("exit: too many arguments", False),
        )

    def test_exit(self):
        self.assertEqual(execute("exit"), ("", True))


if __name__ == "__main__":
    unittest.main()
