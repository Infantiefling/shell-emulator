"""Тесты работы команд с виртуальной файловой системой."""

import unittest

from src.shell import Shell


def sample_vfs():
    """Создать VFS с вложенными каталогами и файлами."""
    return {
        "/": {"type": "dir", "content": b""},
        "/home": {"type": "dir", "content": b""},
        "/home/user": {"type": "dir", "content": b""},
        "/home/user/docs": {"type": "dir", "content": b""},
        "/home/user/docs/a.txt": {"type": "file", "content": b"abc"},
        "/home/user/b.bin": {"type": "file", "content": b"12345"},
        "/etc": {"type": "dir", "content": b""},
        "/etc/config": {"type": "file", "content": b"xy"},
    }


class CommandTests(unittest.TestCase):
    """Проверить команды, пути и сохраняемое состояние."""

    def setUp(self):
        self.shell = Shell(sample_vfs())

    def test_ls_root(self):
        self.assertEqual(self.shell.execute("ls"), ("etc\nhome", False))

    def test_ls_nested(self):
        self.assertEqual(self.shell.execute("ls /home/user"),
                         ("b.bin\ndocs", False))


    def test_ls_missing(self):
        self.assertIn("no such file", self.shell.execute("ls /no")[0])

    def test_cd_and_pwd(self):
        self.assertEqual(self.shell.execute("cd home"), ("", False))
        self.assertEqual(self.shell.execute("pwd"), ("/home", False))

    def test_cd_relative_and_parent(self):
        self.shell.execute("cd /home/user/docs")
        self.shell.execute("cd ..")
        self.assertEqual(self.shell.execute("pwd"), ("/home/user", False))


    def test_cd_file(self):
        self.assertIn("not a directory",
                      self.shell.execute("cd /etc/config")[0])
        self.assertEqual(self.shell.cwd, "/")


    def test_du_file(self):
        self.assertEqual(self.shell.execute("du /home/user/b.bin"),
                         ("5\t/home/user/b.bin", False))

    def test_du_directory_recursive(self):
        self.assertEqual(self.shell.execute("du /home/user"),
                         ("8\t/home/user", False))


    def test_du_relative(self):
        self.shell.execute("cd /home/user")
        self.assertEqual(self.shell.execute("du docs"),
                         ("3\t/home/user/docs", False))


    def test_history(self):
        self.shell.execute("pwd")
        self.shell.execute("ls /etc")
        output, _ = self.shell.execute("history")
        self.assertEqual(output, "1  pwd\n2  ls /etc\n3  history")

    def test_history_includes_errors(self):
        self.shell.execute("nonsense")
        self.assertIn("nonsense", self.shell.execute("history")[0])


    def test_wrong_argument_count(self):
        for command in ("ls", "cd", "pwd", "du", "history"):
            self.assertIn("too many arguments",
                          self.shell.execute(f"{command} a b")[0])

    def test_no_disk_changes(self):
        original = sample_vfs()
        self.shell.execute("cd /home/user")
        self.shell.execute("ls")
        self.shell.execute("du")
        self.assertEqual(self.shell.vfs, original)


if __name__ == "__main__":
    unittest.main()
