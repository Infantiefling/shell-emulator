"""Чтение аргументов командной строки и XML-конфигурации."""

import argparse
from pathlib import Path
import xml.etree.ElementTree as ET


class Config:
    """Хранить параметры конфигурации эмулятора."""

    def __init__(self, vfs=None, script=None, config=None):
        self.vfs = vfs
        self.script = script
        self.config = config


def parse_arguments(argv=None):
    """Прочитать параметры командной строки."""
    parser = argparse.ArgumentParser(description="Shell emulator")
    parser.add_argument("--vfs", help="Path to the VFS file")
    parser.add_argument("--script", help="Path to the startup script")
    parser.add_argument("--config", help="Path to the XML config")
    return parser.parse_args(argv)


def read_xml(path):
    """Прочитать настройки из XML-файла."""
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        raise ValueError(f"Cannot load configuration: {error}") from error

    if root.tag != "config":
        raise ValueError("Configuration root must be <config>")

    return {
        "vfs": root.findtext("vfs"),
        "script": root.findtext("script"),
    }


def load_config(argv=None):
    """Загрузить настройки с приоритетом XML над аргументами."""
    args = parse_arguments(argv)
    vfs = args.vfs
    script = args.script

    if args.config:
        values = read_xml(args.config)
        if values["vfs"] is not None:
            vfs = values["vfs"].strip() or None
        if values["script"] is not None:
            script = values["script"].strip() or None

    return Config(vfs=vfs, script=script, config=args.config)


def read_startup_script(path):
    """Прочитать команды, пропуская пустые строки и комментарии."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise ValueError(f"Cannot load script: {error}") from error

    commands = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            commands.append(line)
    return commands
