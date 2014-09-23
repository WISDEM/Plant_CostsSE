"""
test_Plant_CostsSE.py

Created by Katherine Dykes on 2014-01-07.
Copyright (c) NREL. All rights reserved.
"""

import unittest
from commonse.utilities import check_gradient_unit_test
#from nrel_onshore_bos.nrel_bos_onshore import bos_nrel_onshore_component
from plant_costsse.nrel_csm_bos.nrel_csm_bos import bos_csm_component, bos_csm_assembly
from plant_costsse.nrel_csm_opex.nrel_csm_opex import opex_csm_component, opex_csm_assembly


# Plant Costs - BOS

''' # NREL Land-Based BOS Model
class Test_bos_nrel_onshore_component(unittest.TestCase):

    def test_gradient(self):

        bos = bos_nrel_onshore_component()
        bos.machine_rating = 5000.0
        bos.rotor_diameter = 126.0
        bos.turbine_cost = 5950209.283
        bos.turbine_number = 100
        bos.hub_height = 90.0
        bos.RNA_mass = 256634.5

        check_gradient_unit_test(self, bos)'''

# NREL_CSM_BOS

class Test_bos_csm_assembly(unittest.TestCase):

    def setUp(self):

        self.bos = bos_csm_assembly()
        self.bos.machine_rating = 5000.0
        self.bos.rotor_diameter = 126.0
        self.bos.turbine_cost = 5950209.28
        self.bos.turbine_number = 100
        self.bos.hub_height = 90.0
        self.bos.RNA_mass = 256634.5  # RNA mass is not used in this simple model

    def test_functionality(self):
        
        self.bos.run()
        
        self.assertEqual(round(self.bos.bos_costs,2), 766464743.61)

class Test_bos_csm_component(unittest.TestCase):

    def setUp(self):

        self.bos = bos_csm_component()
        self.bos.machine_rating = 5000.0
        self.bos.rotor_diameter = 126.0
        self.bos.turbine_cost = 5950209.28
        self.bos.turbine_number = 100
        self.bos.hub_height = 90.0
        self.bos.RNA_mass = 256634.5  # RNA mass is not used in this simple model

    def test_functionality(self):
        
        self.bos.run()
        
        self.assertEqual(round(self.bos.bos_costs,2), 766464743.61)

    def test_gradient(self):

        check_gradient_unit_test(self, self.bos, display=False)


# Plant Costs - OPEX

#NREL CSM OPEX
class Test_om_csm_assembly(unittest.TestCase):

    def setUp(self):

        self.om = opex_csm_assembly()

        self.om.machine_rating = 5000.0
        self.om.net_aep = 1701626526.28
        self.om.sea_depth = 20.0
        self.om.year = 2009
        self.om.month = 12
        self.om.turbine_number = 100

    def test_functionality(self):
        
        self.om.run()
        
        self.assertEqual(round(self.om.avg_annual_opex,1), 47575391.9)

class Test_om_csm_component(unittest.TestCase):

    def setUp(self):

        self.om = opex_csm_component()

        self.om.machine_rating = 5000.0
        self.om.net_aep = 1701626526.28
        self.om.sea_depth = 20.0
        self.om.year = 2009
        self.om.month = 12
        self.om.turbine_number = 100

    def test_functionality(self):
        
        self.om.run()
        
        self.assertEqual(round(self.om.avg_annual_opex,1), 47575391.9)

    def test_gradient(self):

        check_gradient_unit_test(self, self.om)

if __name__ == "__main__":
    unittest.main()
