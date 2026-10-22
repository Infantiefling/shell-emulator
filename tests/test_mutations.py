"""Тесты удаления и перемещения элементов виртуальной файловой системы."""

import unittest

from src.shell import Shell
from src.vfs import load_vfs


class MutationTests(unittest.TestCase):
    """Проверить изменения VFS исключительно в памяти."""

    def setUp(self):
        self.shell = Shell(load_vfs("examples/sample.csv"))

    def test_remove_empty_directory(self):
        self.shell.vfs["/empty"] = {"type": "dir", "content": b""}
        self.assertEqual(self.shell.execute("rmdir /empty"), ("", False))
        self.assertNotIn("/empty", self.shell.vfs)

    def test_remove_nonempty_directory(self):
        result, _ = self.shell.execute("rmdir /home/user/docs")
        self.assertIn("not empty", result)
        self.assertIn("/home/user/docs", self.shell.vfs)

    def test_remove_root_and_current_directory(self):
        self.assertIn("cannot remove", self.shell.execute("rmdir /")[0])
        self.shell.execute("cd /home/user")
        self.assertIn("cannot remove", self.shell.execute("rmdir .")[0])

    def test_rmdir_invalid_target(self):
        self.assertIn("no such directory",
                      self.shell.execute("rmdir /missing")[0])
        self.assertIn("not a directory",
                      self.shell.execute("rmdir /etc/config.txt")[0])

    def test_rename_file(self):
        before = self.shell.vfs["/etc/config.txt"]["content"]
        self.assertEqual(self.shell.execute(
            "mv /etc/config.txt /etc/renamed.txt"), ("", False))
        self.assertNotIn("/etc/config.txt", self.shell.vfs)
        self.assertEqual(self.shell.vfs["/etc/renamed.txt"]["content"], before)

    def test_move_file_into_directory(self):
        self.shell.execute("mv /etc/config.txt /home/user/docs")
        self.assertIn("/home/user/docs/config.txt", self.shell.vfs)
        self.assertNotIn("/etc/config.txt", self.shell.vfs)

    def test_move_directory_with_children(self):
        self.shell.execute("mv /home/user/docs /etc/docs")
        self.assertIn("/etc/docs/notes.txt", self.shell.vfs)
        self.assertIn("/etc/docs/photo.bin", self.shell.vfs)
        self.assertNotIn("/home/user/docs", self.shell.vfs)

    def test_move_updates_current_directory(self):
        self.shell.execute("cd /home/user/docs")
        self.shell.execute("mv /home/user /etc/member")
        self.assertEqual(self.shell.execute("pwd"),
                         ("/etc/member/docs", False))

    def test_reject_move_into_itself(self):
        result, _ = self.shell.execute(
            "mv /home/user /home/user/docs/child")
        self.assertIn("into itself", result)
        self.assertIn("/home/user/docs", self.shell.vfs)

    def test_reject_existing_target(self):
        result, _ = self.shell.execute(
            "mv /etc/config.txt /home/user/docs/notes.txt")
        self.assertIn("already exists", result)
        self.assertIn("/etc/config.txt", self.shell.vfs)

    def test_reject_invalid_destination_and_root(self):
        self.assertIn("no such directory", self.shell.execute(
            "mv /etc/config.txt /missing/file.txt")[0])
        self.assertIn("cannot move root", self.shell.execute(
            "mv / /root")[0])

    def test_wrong_argument_count(self):
        self.assertIn("expected source", self.shell.execute("mv /home")[0])
        self.assertIn("missing directory", self.shell.execute("rmdir")[0])
        self.assertIn("too many arguments", self.shell.execute(
            "rmdir /etc /home")[0])

    def test_file_is_unchanged_on_disk(self):
        path = "examples/sample.csv"
        with open(path, "rb") as file:
            before = file.read()
        self.shell.execute("mv /etc/config.txt /etc/new.txt")
        self.shell.execute("rmdir /home/user/docs")
        with open(path, "rb") as file:
            self.assertEqual(file.read(), before)


if __name__ == "__main__":
    unittest.main()
