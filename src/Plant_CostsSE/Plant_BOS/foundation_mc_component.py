"""
foundation_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from twister.models.bos.foundation.foundation import foundation

class foundation_mc_component(Component):
    """
       Component to wrap python code for monopile foundation mass-cost model
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    ratedPower = Float(5000.0, units = 'kW', iotype='in', desc=' rated power of machine')
    monopileMass = Float(1678575.888, units='lb', iotype='in', desc = 'monopile total mass for primary steel')
    transitionMass = Float(913000.00, units='lb', iotype='in', desc = 'transition piece total mass')
   
    # Plant Configuration
    seaDepth = Float(0.0, units = 'm', iotype='in', desc = 'project site water depth')

    # ------------- Outputs -------------- 
  
    foundationCost = Float(0.0, units='USD', iotype='out', desc='cost for a foundation')

    def __init__(self):
        """
        OpenMDAO component to wrap foundation mass-cost model based on NREL BOS Offshore Model (foundation.py)

        Parameters
        ---------- 
		    ratedPower : float
		      rated power of machine [kW]
		    monopileMass : float
		      monopile total mass for primary steel [kg]
		    transitionMass : float
		      transition piece total mass [kg]
		    seaDepth : float
		      project site water depth [m]
		      
		    Returns
		    -------
    		foundationCost : float
    		  cost for a foundation [USD]  
        """
        super(foundation_mc_component, self).__init__()
        
        self.foundation = foundation()

    def execute(self):
        """
        Executes a monopile mass-cost model based on the NREL BOS Offshore Excel model and determines foundation cost.
        """

        print "In {0}.execute()...".format(self.__class__)
        
        self.foundation.compute(self.ratedPower, self.seaDepth, self.monopileMass, self.transitionMass)

        self.foundationCost = self.foundation.getCost()
           
#-----------------------------------------------------------------

def example():

    # simple test of module

    fdn = foundation_mc_component()
        
    # First test
    fdn.ratedPower = 5000.0
    fdn.seaDepth = 20.0
    fdn.monopileMass = 763000.0
    fdn.transitionMass = 415000.0
    
    fdn.execute()

    print "Foundation cost: {0}".format(fdn.foundationCost)

if __name__ == "__main__":

    example()