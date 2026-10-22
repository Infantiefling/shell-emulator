"""Тесты разбора и выполнения команд оболочки."""

import unittest

from src.shell import Shell, parse_command
from src.vfs import create_default_vfs


class ParserTests(unittest.TestCase):
    """Проверить разделение команд и аргументов."""

    def test_command_without_arguments(self):
        self.assertEqual(parse_command("ls"), ("ls", []))

    def test_command_with_arguments(self):
        self.assertEqual(parse_command("ls folder file"),
                         ("ls", ["folder", "file"]))

    def test_extra_whitespace(self):
        self.assertEqual(parse_command("  cd   documents  "),
                         ("cd", ["documents"]))

    def test_empty_input(self):
        self.assertEqual(parse_command("   "), ("", []))


class ShellTests(unittest.TestCase):
    """Проверить обработку команд на минимальной VFS."""

    def setUp(self):
        self.shell = Shell(create_default_vfs())

    def test_empty_input(self):
        self.assertEqual(self.shell.execute("   "), ("", False))

    def test_unknown_command(self):
        self.assertEqual(self.shell.execute("oops"),
                         ("oops: command not found", False))

    def test_invalid_arguments(self):
        for command in ("ls", "cd", "du", "pwd", "history", "exit"):
            self.assertEqual(self.shell.execute(f"{command} a b"),
                             (f"{command}: too many arguments", False))

    def test_exit(self):
        self.assertEqual(self.shell.execute("exit"), ("", True))


if __name__ == "__main__":
    unittest.main()
