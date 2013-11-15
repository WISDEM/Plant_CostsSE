"""
fin_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, Enum, VarTree

from twister.models.csm.csmFinance import csmFinance 

class fin_csm_component(Component):    

    # ---- Design Variables --------------    
    # Turbine configuration
    # rotor
    ratedPower = Float(5000.0, units = 'kW', iotype = 'in', desc = 'rated power for a wind turbine')
    
    # Plant Configuration
    fixedChargeRate = Float(0.12, iotype = 'in', desc = 'fixed charge rate for coe calculation')
    constructionFinancingRate = Float(0.00, iotype='in', desc = 'construction financing rate applied to overnight capital costs')
    taxRate = Float(0.4, iotype = 'in', desc = 'tax rate applied to operations')
    discountRate = Float(0.07, iotype = 'in', desc = 'applicable project discount rate')
    constructionTime = Float(1.0, iotype = 'in', desc = 'number of years to complete project construction')
    projectLifetime = Float(20.0, iotype = 'in', desc = 'project lifetime for LCOE calculation')
    turbineNumber = Int(100, iotype = 'in', desc = 'number of turbines at plant')
    aep              = Float(245869523.851, iotype='in', units='kW * h', desc='Annual energy production') 
    turbineCost         = Float(9000000.00, iotype='in', units='USD', desc='Turbine capital costs')
    BOScost          = Float(29893055.879, iotype='in', units='USD', desc='Balance of station costs')
    preventativeMaintenanceCost = Float(1888344.846, iotype='in', units='USD', desc='O&M costs')
    correctiveMaintenanceCost   = Float(880488.338, iotype='in', units='USD', desc='levelized replacement costs')
    landLeaseCost     = Float(291344.633, iotype='in', units='USD', desc='land lease costs')  
    seaDepth = Float(20.0, iotype='in', units='m', desc = 'depth of project for offshore, (0 for onshore)')
        
    # ------------- Outputs --------------     

    coe              = Float(0.0, iotype='out', desc='Cost of energy - unlevelized')
    lcoe             = Float(0.0, iotype='out', desc='Cost of energy - levelized')

    
    def __init__(self):
        """
        OpenMDAO component to wrap finance model of the NREL Cost and Scaling Model (csmFinance.py)

        Parameters
        ----------  
		    ratedPower : float
		      rated power for a wind turbine [kW]
		    fixedChargeRate : float
		      fixed charge rate for coe calculation
		    constructionFinancingRate : float
		      construction financing rate applied to overnight capital costs
		    taxRate : float
		      tax rate applied to operations
		    discountRate : float
		      applicable project discount rate
		    constructionTime : float
		      number of years to complete project construction
		    projectLifetime : float
		      project lifetime for LCOE calculation
		    turbineNumber : int
		      number of turbines at plant
		    aep : float
		      Annual energy production [kWh]
		    turbineCost : float
		      Turbine capital costs [USD per turbine]
		    BOScost : float
		      Balance of station costs total [USD]
		    preventativeMaintenanceCost : float
		      O&M costs annual total [USD]
		    correctiveMaintenanceCost : float
		      levelized replacement costs annual total [USD]
		    landLeaseCost : float
		      land lease costs annual total [USD] 
		    seaDepth : float
		      depth of project [m]
		        
        Returns
        -------
		    coe : float
		      Cost of energy - unlevelized [USD/kWh]
		    lcoe : float
		      Cost of energy - levelized [USD/kWh]

        """

        super(fin_csm_component, self).__init__()

        #initialize csmFIN model
        self.fin = csmFinance()


    def execute(self):
        """
        Executes finance model of the NREL Cost and Scaling model to determine overall plant COE and LCOE.
        """
        
        print "In {0}.execute()...".format(self.__class__)

        self.fin.compute(self.ratedPower, self.turbineCost * self.turbineNumber, self.preventativeMaintenanceCost, self.landLeaseCost, self.correctiveMaintenanceCost, self.BOScost, self.aep, \
                         self.fixedChargeRate, self.constructionFinancingRate, self.taxRate, self.discountRate, self.constructionTime, \
                         self.projectLifetime, self.turbineNumber, self.seaDepth)

        self.coe = self.fin.getCOE()
        self.lcoe = self.fin.getLCOE()

def example():
	
    # simple test of module

    fin = fin_csm_component()

    fin.execute()
    print "Onshore"
    print "lcoe: {0}".format(fin.lcoe)
    print "coe: {0}".format(fin.coe)

    fin.turbineCost = 1794724.6
    OnMcost = 5267299.667
    OnMllc = 291344.633
    OnMlrc = 1364725.806
    fin.avg_annual_opex = OnMcost + OnMllc + OnMlrc
    fin.bos_cost = 97150303.809 + 12236758.693
    
    fin.execute()
    print "Offshore"
    print "lcoe: {0}".format(fin.lcoe)
    print "coe: {0}".format(fin.coe)	

if __name__ == "__main__":

    example()