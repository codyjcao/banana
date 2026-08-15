#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Keep unit tests scoped to concrete submodules.

The public `banana` and `banana.monitors` package exports are covered by
an explicit import test. Most tests import concrete modules so they can
still run and report focused failures when a package-level export breaks.
"""

from pathlib import Path
import sys
import types


_SRC_BANANA = Path(__file__).resolve().parents[1] / "src" / "banana"


def _install_namespace_package(name: str, path: Path) -> None:
    module = types.ModuleType(name)
    module.__path__ = [str(path)]
    sys.modules[name] = module


_install_namespace_package("banana", _SRC_BANANA)
_install_namespace_package("banana.monitors", _SRC_BANANA / "monitors")
