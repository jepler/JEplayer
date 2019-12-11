#!/usr/bin/python
import os
import shutil
import subprocess
from circuitpython_build_tools.build import mpy_cross
mpy_cross(".venv/bin/mpy-cross", "master")

def copy(destdir, srcdir, name, *, destname=None):
    print("# COPY", destdir, name)
    if destname is None: destname = name
    shutil.copy(os.path.join(srcdir, name), os.path.join(destdir, destname))

def mpy_compile(destdir, srcdir, name, *, destname=None):
    print("# CROSS", destdir, name)
    if destname is None: destname = os.path.splitext(name)[0] + ".mpy"
    subprocess.run(['.venv/bin/mpy-cross', "-o",
            os.path.join(destdir, destname),
            os.path.join(srcdir, name)], check=True)

def put(dest, content):
    with open(dest, "w") as f: f.write(content)
SRCPATH = 'src'
DSTPATH = 'CIRCUITPY'

for dirpath, dirnames, filenames in os.walk('src', followlinks=True):
    outpath = os.path.join(DSTPATH, os.path.relpath(dirpath, SRCPATH))
    print(outpath)
    os.makedirs(outpath, exist_ok=True)

    for f in filenames:
        if f.startswith('.'): continue
        if dirpath == SRCPATH and f in ('code.py', 'main.py'):
            print("REALMAIN")
            mpy_compile(outpath, dirpath, f, destname="realmain.mpy")
        elif f.endswith('.py'): mpy_compile(outpath, dirpath, f)
        else: copy(outpath, dirpath, f)
put("CIRCUITPY/main.py", "import realmain\n")
