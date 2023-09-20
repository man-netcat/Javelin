#!/usr/bin/env python3

import os
import shutil
import subprocess

icon = "javelin.ico"
exe = "Javelin.exe"

subprocess.run(
    [
        "pyinstaller",
        "--onefile",
        f"--icon={icon}",
        "--noconsole",
        "javelin.py",
    ]
)

dist_path = "dist"
javelin_exe = os.path.join(dist_path, exe)
root_javelin_exe = exe

shutil.move(javelin_exe, root_javelin_exe)
shutil.rmtree(dist_path)
shutil.rmtree("build")

print("Build process completed.")
