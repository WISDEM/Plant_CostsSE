#
# This file is autogenerated during plugin quickstart and overwritten during
# plugin makedist. DO NOT CHANGE IT if you plan to use plugin makedist to update 
# the distribution.
#

from setuptools import setup, find_packages

kwargs = {'author': '',
 'author_email': '',
 'classifiers': ['Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering'],
 'description': '',
 'download_url': '',
 'include_package_data': True,
 'install_requires': ['openmdao.main'],
 'keywords': ['openmdao'],
 'license': '',
 'maintainer': '',
 'maintainer_email': '',
 'name': 'plant_costsse',
 'package_data': {'plant_costsse': []},
 'package_dir': {'': 'src'},
 'packages': ['plant_costsse'],
 'url': '',
 'version': '0.1.1',
 'zip_safe': False}


setup(**kwargs)

# set up for landbased bos model
from distutils.core import setup
from distutils.extension import Extension

try:
    USE_CYTHON = True
    from Cython.Build import cythonize
except Exception:
    USE_CYTHON = False


ext = '.pyx' if USE_CYTHON else '.c'

extensions = [Extension('_landbos', ['src/plant_costsse/nrel_land_bosse/_landbos'+ext, 'src/plant_costsse/nrel_land_bosse/LandBOSsmooth.c'])]

if USE_CYTHON:
    extensions = cythonize(extensions)

setup(
    name='NREL_Land_BOSSE',
    description='a translation of the NREL landbased balance of station excel model',
    author='NREL WISDEM Team',
    author_email='systems.engineering@nrel.gov',
    package_dir={'': 'src'},
    py_modules=['plant_costsse.nrel_land_bosse.nrel_land_bosse'],
    license='Apache License, Version 2.0',
    ext_modules=extensions
)
