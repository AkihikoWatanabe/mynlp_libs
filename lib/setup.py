# coding=utf-8

from distutils.core import setup, Extension
from Cython.Build import cythonize

ext = Extension("cutils",
        sources=["cutils.pyx"],
        language="c++")
setup(
    name = "cutils",
    ext_modules = cythonize(ext)
)
