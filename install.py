#!/usr/bin/python
import os
import shutil
import subprocess

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
        copy(outpath, dirpath, f)
