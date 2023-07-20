#!/usr/bin/env python3

import os
import re

from pathlib import Path
from setuptools import find_packages
from setuptools import setup
from setuptools.command.install_lib import install_lib


class InstallLib(install_lib):

    def install(self):
        # Patch installation paths into catapult/__init__.py.
        prefix = os.getenv("CATAPULT_PREFIX", "/usr/local")
        data_dir = Path(prefix) / "share" / "catapult"
        locale_dir = Path(prefix) / "share" / "locale"
        init_path = Path(self.build_dir) / "catapult" / "__init__.py"
        init_text = init_path.read_text("utf-8")
        patt = r"^DATA_DIR = .*$"
        repl = f"DATA_DIR = Path({str(data_dir)!r})"
        init_text = re.sub(patt, repl, init_text, flags=re.MULTILINE)
        assert init_text.count(repl) == 1
        patt = r"^LOCALE_DIR = .*$"
        repl = f"LOCALE_DIR = Path({str(locale_dir)!r})"
        init_text = re.sub(patt, repl, init_text, flags=re.MULTILINE)
        assert init_text.count(repl) == 1
        init_path.write_text(init_text, "utf-8")
        return install_lib.install(self)


def get_version(fm="catapult/__init__.py"):
    for line in Path(fm).read_text("utf-8").splitlines():
        if line.startswith("__version__ = "):
            return line.split()[-1].strip('"')

assert get_version()

setup(
    name="catapult",
    version=get_version(),
    packages=find_packages(exclude=["*.test"]),
    scripts=["bin/catapult-start"],
    cmdclass={"install_lib": InstallLib},
)
