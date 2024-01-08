#!/usr/bin/env python

import http.client
import json
import os
import os.path
import shutil
import subprocess
import sys
from urllib.parse import urlparse
from pathlib import Path


project_root = Path(__file__).parent.resolve()


def command_dependencies():
    """ installs the dependencies via virtualenv and pip.
    """
    if not (project_root / "venv").exists():
        return

    shell(["virtualenv", "venv"])
    shell(["pip", "install", "--requirement", "requirements.txt"])


def command_build():
    """
    """
    command_dependencies()
    shell(['python', 'convert.py'])


def command_clean():
    """cleans the project dir"""
    for name in ["venv", "build"]:
        shutil.rmtree(name, ignore_errors=True)


def command_help():
    """displays the help message"""
    print("usage: build <command> [<args>...]")
    print("")
    print("commands:")
    width = max(len(name) for name in commands.keys())
    for name, func in commands.items():
        summary = (func.__doc__ or "").split("\n")[0].strip()
        print("  %s - %s" % (name.ljust(width), summary))


class ShellError(RuntimeError):
    pass


def shell(args, env={}):
    path = os.pathsep.join([
        str(project_root / "venv" / "Scripts"),
        str(project_root / "venv" / "bin"),
        str(project_root / "node_modules" / ".bin"),
        os.environ["PATH"],
    ])

    pythonpath = os.pathsep.join([
        str(project_root),
        os.environ.get("PYTHONPATH", ""),
    ])

    exe = shutil.which(args[0], path=path)

    try:
        subprocess.run(
            [exe] + args[1:],
            check=True,
            env={
                **os.environ,
                **env,
                "PYTHONPATH": pythonpath,
                "PATH": path,
            },
            capture_output=False,
        )
    except Exception as exc:
        raise ShellError(exc)


commands = dict(
    (name[len("command_") :], func)
    for name, func in globals().items()
    if name.startswith("command_")
)


def main(args):
    try:
        if not args or args[0] not in commands:
            command_help()
        else:
            commands[args[0]](*args[1:])
    except ShellError as err:
        print(err)
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])
