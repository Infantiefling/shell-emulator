"""Тесты аргументов командной строки и XML-конфигурации."""

import tempfile
import unittest
from pathlib import Path

from src.config import load_config, read_startup_script


class ConfigTests(unittest.TestCase):
    """Проверить загрузку и приоритет параметров."""

    def test_defaults(self):
        config = load_config([])
        self.assertIsNone(config.vfs)
        self.assertIsNone(config.script)

    def test_cli_parameters(self):
        config = load_config(["--vfs", "disk.csv", "--script", "run.txt"])
        self.assertEqual(config.vfs, "disk.csv")
        self.assertEqual(config.script, "run.txt")

    def test_xml_overrides_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.xml"
            path.write_text(
                "<config><vfs>file.csv</vfs>"
                "<script>file.txt</script></config>",
                encoding="utf-8",
            )
            config = load_config([
                "--vfs", "cli.csv", "--script", "cli.txt",
                "--config", str(path),
            ])
        self.assertEqual(config.vfs, "file.csv")
        self.assertEqual(config.script, "file.txt")

    def test_xml_partial_override(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.xml"
            path.write_text("<config><vfs>file.csv</vfs></config>")
            config = load_config([
                "--vfs", "cli.csv", "--script", "cli.txt",
                "--config", str(path),
            ])
        self.assertEqual(config.vfs, "file.csv")
        self.assertEqual(config.script, "cli.txt")

    def test_missing_config(self):
        with self.assertRaises(ValueError):
            load_config(["--config", "missing_config_123.xml"])

    def test_invalid_xml(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.xml"
            path.write_text("<config>")
            with self.assertRaises(ValueError):
                load_config(["--config", str(path)])

    def test_startup_comments(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "startup.txt"
            path.write_text("# comment\nls\n\n  # skip\ncd docs\n")
            commands = read_startup_script(path)
        self.assertEqual(commands, ["ls", "cd docs"])

    def test_missing_script(self):
        with self.assertRaises(ValueError):
            read_startup_script("missing_script_123.txt")


if __name__ == "__main__":
    unittest.main()
