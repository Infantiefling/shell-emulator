"""Загрузка виртуальной файловой системы из CSV в память."""

import base64
import binascii
import csv
from pathlib import Path


class VFSError(ValueError):
    """Ошибка загрузки или структуры виртуальной файловой системы."""


def create_default_vfs():
    """Создать минимальную VFS, если файл не задан."""
    return {"/": {"type": "dir", "content": b""}}


def check_path(path):
    """Проверить формат абсолютного пути внутри VFS."""
    if not path.startswith("/") or "\\" in path:
        raise VFSError(f"Invalid VFS path: {path}")
    if path != "/" and (path.endswith("/") or "//" in path):
        raise VFSError(f"Invalid VFS path: {path}")
    if path == "/":
        return
    parts = path.split("/")[1:]
    if any(part in ("", ".", "..") for part in parts):
        raise VFSError(f"Invalid VFS path: {path}")


def read_entry(row):
    """Проверить одну строку CSV и преобразовать её в запись VFS."""
    path = row["path"]
    kind = row["type"]
    encoded = row["content"]
    if path is None or kind is None or encoded is None:
        raise VFSError("Invalid VFS format: incomplete row")
    check_path(path)
    if kind not in ("dir", "file"):
        raise VFSError(f"Invalid VFS type: {kind}")
    if kind == "dir" and encoded:
        raise VFSError(f"Directory cannot have content: {path}")
    try:
        content = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as error:
        raise VFSError(f"Invalid base64 content: {path}") from error
    return path, {"type": kind, "content": content}


def check_structure(vfs):
    """Проверить наличие корня и родительских каталогов."""
    if "/" not in vfs or vfs["/"]["type"] != "dir":
        raise VFSError("Invalid VFS: missing root directory")
    for path in vfs:
        if path == "/":
            continue
        parent = path.rsplit("/", 1)[0] or "/"
        if parent not in vfs or vfs[parent]["type"] != "dir":
            raise VFSError(f"Invalid VFS parent: {path}")


def load_vfs(path=None):
    """Загрузить CSV в словарь или создать VFS по умолчанию."""
    if not path:
        return create_default_vfs()
    try:
        with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, strict=True)
            if reader.fieldnames != ["path", "type", "content"]:
                raise VFSError("Invalid VFS format: CSV columns")
            vfs = {}
            for row in reader:
                if None in row:
                    raise VFSError("Invalid VFS format: extra CSV fields")
                item_path, entry = read_entry(row)
                if item_path in vfs:
                    raise VFSError(f"Duplicate VFS path: {item_path}")
                vfs[item_path] = entry
    except (OSError, UnicodeError, csv.Error) as error:
        raise VFSError(f"Cannot load VFS: {error}") from error
    check_structure(vfs)
    return vfs
