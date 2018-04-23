from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy

extensions = [
        Extension('memosim_ext.mosaik_v2',
            ['memosim_ext/mosaik_v2.pyx'],
            include_dirs=[numpy.get_include()]),
        Extension('memosim_ext.simulation_v2',
            ['memosim_ext/simulation_v2.pyx'],
            include_dirs=[numpy.get_include()]),
]

setup(
    name="MeMoSim-py",
    version='1.0',
    author='Thole Klingenberg',
    author_email='thole.klingenberg@offis.de',
    setup_requires=['nose>=1.0'],
    test_suite='nose.collector',
    packages=find_packages(),
    ext_modules=cythonize(extensions),
    install_requires=[
        'numpy>=1.6',
    ],
)
