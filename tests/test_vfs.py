"""Тесты загрузки виртуальной файловой системы."""

import tempfile
import unittest
from pathlib import Path

from src.vfs import VFSError, load_vfs


class VFSTests(unittest.TestCase):
    """Проверить загрузку CSV и обработку ошибок VFS."""

    def load_text(self, text):
        """Записать CSV во временный файл и прочитать VFS."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vfs.csv"
            path.write_text(text, encoding="utf-8")
            return load_vfs(path)

    def test_default_vfs(self):
        self.assertEqual(load_vfs(), {
            "/": {"type": "dir", "content": b""},
        })

    def test_minimal_vfs(self):
        vfs = load_vfs("examples/minimal.csv")
        self.assertEqual(list(vfs), ["/"])

    def test_files_and_binary(self):
        vfs = load_vfs("examples/files.csv")
        self.assertEqual(vfs["/readme.txt"]["content"], b"Readme text")
        self.assertEqual(vfs["/numbers.bin"]["content"], b"\0\1\2\xff")

    def test_nested_directories(self):
        vfs = load_vfs("examples/nested.csv")
        self.assertIn("/home/user/docs/notes.txt", vfs)
        self.assertEqual(vfs["/home/user/docs"]["type"], "dir")

    def test_file_is_not_modified(self):
        path = Path("examples/sample.csv")
        before = path.read_bytes()
        load_vfs(path)
        self.assertEqual(path.read_bytes(), before)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(VFSError):
                load_vfs(Path(directory) / "missing.csv")

    def test_wrong_columns(self):
        with self.assertRaises(VFSError):
            self.load_text("name,kind,data\n/,dir,\n")

    def test_invalid_base64(self):
        with self.assertRaises(VFSError):
            self.load_text("path,type,content\n/,dir,\n/x,file,%%%\n")

    def test_missing_parent(self):
        with self.assertRaises(VFSError):
            self.load_text("path,type,content\n/,dir,\n/a/b,file,QQ==\n")

    def test_parent_is_file(self):
        with self.assertRaises(VFSError):
            self.load_text("path,type,content\n/,dir,\n/a,file,\n/a/b,file,\n")

    def test_duplicate_path(self):
        with self.assertRaises(VFSError):
            self.load_text("path,type,content\n/,dir,\n/a,dir,\n/a,dir,\n")


if __name__ == "__main__":
    unittest.main()
