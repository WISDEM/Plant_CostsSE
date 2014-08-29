Plant_CostsSE is a set of models for analyzing wind plant balance of station and operational expenditures for both land-based and offshore wind plants.

Author: [K. Dykes](mailto:katherine.dykes@nrel.gov)

## Prerequisites

NumPy, SciPy, FUSED-Wind, OpenMDAO

## Installation

Install Turbine_CostsSE within an activated OpenMDAO environment

	$ plugin install

It is not recommended to install the software outside of OpenMDAO.

## Run Unit Tests

To check if installation was successful try to import the module

	$ python
	> import plant_costsse.plant_costsse

You may also run the unit tests.

	$ python src/test/test_Plant_CostsSE_gradients.py

## Detailed Documentation

Online documentation is available at <http://wisdem.github.io/Plant_CostsSE/>