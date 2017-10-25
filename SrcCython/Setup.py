from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("C:/Users/Pedro/PycharmProjects/PyMCNESEmu/Src/main.pyx")
)
