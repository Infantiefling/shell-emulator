# Shell Emulator — Variant 25

A Python GUI prototype of a UNIX-like shell, built with Tkinter.
This repository implements **stage 1 (REPL)** of the assignment.

## Requirements

- Python 3.13 with Tkinter (standard library)
- Windows for the provided `run.bat` launcher

## Run

From the repository root:

```powershell
.\run.bat
```

Or run `py src/main.py`.

## Commands and behavior

- `ls [path]`: stage-1 stub; prints its name and parsed arguments.
- `cd [path]`: stage-1 stub; prints its name and parsed arguments.
- `exit`: closes the window; arguments are rejected.
- Unknown commands produce an error.
- The parser splits input on whitespace; quoting is not supported at this stage.
- `ls` and `cd` accept at most one argument in this prototype.

## Tests

```powershell
py -m unittest discover -s tests -v
```

## Interactive examples

```text
ls
ls docs
cd projects
cd a b
notacommand
exit now
exit
```

The window title is constructed from the current OS username and hostname.
Later stages will add configuration, VFS, and real command behavior.
