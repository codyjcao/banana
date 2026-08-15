#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path
import subprocess
import sys


def test_public_monitors_package_exports_ny_urban_monitor():
    project_root = Path(__file__).resolve().parents[1]
    env = {
        **os.environ,
        "PYTHONPATH": str(project_root / "src"),
    }

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from banana.monitors import NyUrbanAvailabilityMonitor",
        ],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
