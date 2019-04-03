# Plant_CostsSE
## WARNING- This repository is deprecated

Plant_CostsSE is a set of models for analyzing wind plant balance of station and operational expenditures for both land-based and offshore wind plants. (See separate notes on the land-based balance of station model at the bottom of this page).

Author: [NREL WISDEM Team](mailto:systems.engineering@nrel.gov) 

## Documentation

See local documentation in the `docs`-directory or access the online version at <http://wisdem.github.io/Plant_CostsSE/>

## Installation

For detailed installation instructions of WISDEM modules see <https://github.com/WISDEM/WISDEM> or to install Plant_CostsSE by itself do:

    $ python setup.py install

## Run Unit Tests

To check if installation was successful try to import the package:

	$ python
	> import plant_costsse.nrel_csm_bos.nrel_csm_bos
	> import plant_costsse.nrel_csm_opex.nrel_csm_opex
	> import plant_costsse.ecn_opex_offshore.ecn_opex_offshore

Note that you must have the ECN Offshore OPEX model and license in order to use the latter module.  This software contains only the OpenMDAO wrapper for the model.

You may also run the unit tests which include functional and gradient tests.  Analytic gradients are provided for variables only so warnings will appear for missing gradients on model input parameters; these can be ignored.

	$ python src/test/test_Plant_CostsSE.py

If you have the ECN model, you may run the ECN test which checks for a non-zero value for operational expenditures.  You will likely need to modify the code for the ECN model based on the version you have and its particular configuration.

	$ python src/test/test_Plant_CostsSE_ECN.py

For software issues please use <https://github.com/WISDEM/Plant_CostsSE/issues>.  For functionality and theory related questions and comments please use the NWTC forum for [Systems Engineering Software Questions](https://wind.nrel.gov/forum/wind/viewtopic.php?f=34&t=1002).


NREL_LAND_BOSSE
===============

A C version of the NREL land-based balance of station model.  A continuously differentiable version is also implemented for use in gradient-based optimization applications.  The repository also includes a Python wrapper, an OpenMDAO wrapper and a C++ wrapper all using the same core implementation.

### C Implementation:  

All computations are done here.

LandBOS.c  
LandBOS.h

A "smoothed" version is provided for use in gradient-based optimization applications

LandBOSsmooth.c  (uses same header file)

### C++ wrapper:  

An object-oriented wrapper to simplify i/o.  Uses original implementation (LandBOS.c)

LandBOS.cpp  
LandBOS.hpp  
(also maintest.cpp, makefile, just to test running it)


### Python wrapper:  

A one-to-one mapping, making all C functions available from Python.
By default, the smooth version is used.  But this can be swapped by editing
line 23 in setup.py

_landbos.c  (generated from Cython, can be compiled directly as a Python extension)  
_landbos.pyx, c_landbos.pxd (for development use with Cython)  
setup.py (used to install Python module)

### OpenMDAO wrapper:  

An OpenMDAO assembly to facilitate gradient propogation.

landbos.py


### Unit Tests:  
test/test_land_bosse.py (tests core C functionality.  Unit tests run through the Python wrapper.)  
test/test_land_bosse_openmdao.py (tests OpenMDAO workflow)

