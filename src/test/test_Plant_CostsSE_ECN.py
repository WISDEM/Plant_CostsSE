"""
test_Plant_CostsSE.py

Created by Katherine Dykes on 2014-01-07.
Copyright (c) NREL. All rights reserved.
"""

import unittest
import sys
from plant_costsse.ecn_offshore_opex.ecn_offshore_opex import opex_ecn_offshore_component, opex_ecn_assembly

# Plant Costs - OPEX

# ECN Offshore OPEX
class Test_opex_ecn_offshore_component(unittest.TestCase):

    ssfile = "Path to ECN model"

    def setUp(self,model=None):
        print self.ssfile
        self.om = opex_ecn_offshore_component(self.ssfile)

        self.om.machine_rating = 5000.0
        self.om.net_aep = 1701626526.28
        self.om.sea_depth = 20.0
        self.om.year = 2009
        self.om.month = 12
        self.om.turbine_number = 100

    def test_functionality(self):
        
        self.om.run()
        
        self.assertGreater(round(self.om.avg_annual_opex,1), 0.0)

class Test_opex_ecn_assembly(unittest.TestCase):

    ssfile = "Path to ECN model"

    def setUp(self,model=None):
        print self.ssfile
        self.om = opex_ecn_assembly(self.ssfile)

        self.om.machine_rating = 5000.0
        self.om.net_aep = 1701626526.28
        self.om.sea_depth = 20.0
        self.om.year = 2009
        self.om.month = 12
        self.om.turbine_number = 100

    def test_functionality(self):
        
        self.om.run()
        
        self.assertGreater(round(self.om.avg_annual_opex,1), 0.0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        Test_opex_ecn_offshore_component.ssfile = sys.argv.pop()
        Test_opex_ecn_assembly.ssfile = Test_opex_ecn_offshore_component.ssfile

    unittest.main()
