Plant_CostsSE is a set of models for analyzing wind plant balance of station and operational expenditures for both land-based and offshore wind plants.

Author: [K. Dykes](mailto:katherine.dykes@nrel.gov)

## Prerequisites

NumPy, SciPy, FUSED-Wind, OpenMDAO

## Installation

Install PLant_CostsSE within an activated OpenMDAO environment

	$ plugin install

It is not recommended to install the software outside of OpenMDAO.

## Run Unit Tests

To check if installation was successful try to import the module

	$ python
	> import nrel_csm_bos.nrel_csm_bos
	> import nrel_csm_opex.nrel_csm_opex
	> import ecn_opex_offshore.ecn_opex_offshore

Note that you must have the ECN Offshore OPEX model and license in order to use the latter module.  This software contains only the OpenMDAO wrapper for the model.

You may also run the unit tests.

	$ python src/test/test_Plant_CostsSE_gradients.py

## Detailed Documentation

Online documentation is available at <http://wisdem.github.io/Plant_CostsSE/>