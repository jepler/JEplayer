#!/usr/bin/python
import os
import shutil
import subprocess
from circuitpython_build_tools.build import mpy_cross
mpy_cross(".venv/bin/mpy-cross", "master")

def match(dest, content):
    if not os.path.exists(dest): return False
    with open(dest, "rb") as f: destcontent = f.read()
    return content == destcontent

def copy(destdir, srcdir, name, *, destname=None):
    if destname is None: destname = name
    src = os.path.join(srcdir, name)
    dest = os.path.join(destdir, destname)
    with open(src, "rb") as f: content = f.read()
    put(dest, content)

def mpy_compile(destdir, srcdir, name, *, destname=None):
    if destname is None: destname = os.path.splitext(name)[0] + ".mpy"
    desttemp = os.path.join(destdir, destname + ".tmp")
    dest = os.path.join(destdir, destname)
    subprocess.run(['.venv/bin/mpy-cross', "-o", desttemp,
            os.path.join(srcdir, name)], check=True)
    with open(desttemp, "rb") as f: newcontent = f.read()
    if not match(dest, newcontent):
        os.rename(desttemp, dest)
    else:
        os.unlink(desttemp)

def put(dest, content):
    if not match(dest, content):
        with open(dest, "wb") as f: f.write(content)
SRCPATH = 'src'
DSTPATH = 'CIRCUITPY'

for dirpath, dirnames, filenames in os.walk('src', followlinks=True):
    outpath = os.path.join(DSTPATH, os.path.relpath(dirpath, SRCPATH))
    os.makedirs(outpath, exist_ok=True)

    for f in filenames:
        if f.startswith('.'): continue
        if dirpath == SRCPATH and f in ('code.py', 'main.py'):
            mpy_compile(outpath, dirpath, f, destname="realmain.mpy")
        elif f.endswith('.py'): mpy_compile(outpath, dirpath, f)
        else: copy(outpath, dirpath, f)
put("CIRCUITPY/code.py", b"import realmain\n")
