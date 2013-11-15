"""
foundation_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from twister.models.csm.csmFoundation import csmFoundation

class foundation_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine tower
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    rotorDiameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    hubHeight = Float(90.0, units = 'm', iotype='in', desc = 'hub height of machine')
    ratedPower = Float(5000.0, units = 'kW', iotype='in', desc=' rated power of machine')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')
    seaDepth = Float(0.0, units = 'm', iotype='in', desc = 'project site water depth')

    # ------------- Outputs -------------- 
  
    foundationCost = Float(0.0, units='USD', iotype='out', desc='cost for a foundation')

    def __init__(self):
        """
        OpenMDAO component to wrap foundation model of the NREL Cost and Scaling Model (csmFoundation.py)

        Parameters
        ---------- 
		    rotorDiameter : float
		      rotor diameter of the machine [m]
		    hubHeight : float
		      hub height of machine [m]
		    ratedPower : float
		      rated power of machine [kW]
		    year : int
		      year of project start
		    month : int
		      month of project start
		    seaDepth : float
		      project site water depth [m]
		      
		    Returns
		    -------
    		foundationCost : float
    		  cost for a foundation [USD]	    
        """
        super(foundation_csm_component, self).__init__()
        
        self.foundation = csmFoundation()

    def execute(self):
        """
        Executes foundation model of the NREL Cost and Scaling model to determine foundation costs for a land-based or offshore plant.
        """

        print "In {0}.execute()...".format(self.__class__)
        
        self.foundation.compute(self.ratedPower, self.hubHeight, self.rotorDiameter, self.seaDepth, self.year, self.month)

        self.foundationCost = self.foundation.getCost()
           
#-----------------------------------------------------------------

def example():

    # simple test of module

    fdn = foundation_csm_component()
        
    # First test
    fdn.ratedPower = 5000.0
    fdn.rotorDiameter = 126.0
    fdn.hubHeight = 90.0
    fdn.seaDepth = 0.0
    fdn.year = 2009
    fdn.month = 12
    
    fdn.execute()

    print "Onshore foundation"
    print "Foundation cost: {0}".format(fdn.foundationCost)
    
    fdn.seaDepth = 20.0
    
    fdn.execute()

    print "Offshore foundation"    
    print "Foundation cost: {0}".format(fdn.foundationCost)

if __name__ == "__main__":

    example()