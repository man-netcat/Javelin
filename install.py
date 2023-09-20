#!/usr/bin/env python3

import os
import shutil
import subprocess

subprocess.run(["pyinstaller", "--onefile", "javelin.py", "--icon=javelin.ico"])

dist_path = "dist"
javelin_exe = os.path.join(dist_path, "Javelin.exe")
root_javelin_exe = "Javelin.exe"

shutil.move(javelin_exe, root_javelin_exe)

shutil.rmtree(dist_path)
shutil.rmtree("build")

print("Build process completed.")
