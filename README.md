Plant_CostsSE is a set of models for analyzing wind plant balance of station and operational expenditures for both land-based and offshore wind plants.

Author: [K. Dykes](mailto:katherine.dykes@nrel.gov)

## Version

This software is a beta version 0.1.0.

## Detailed Documentation

For detailed documentation see <http://wisdem.github.io/Plant_CostsSE/>

## Prerequisites

NumPy, SciPy, FUSED-Wind, OpenMDAO, CommonSE

## Installation

Install PLant_CostsSE within an activated OpenMDAO environment

	$ plugin install

It is not recommended to install the software outside of OpenMDAO.

## Run Unit Tests

To check if installation was successful try to import the module

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

