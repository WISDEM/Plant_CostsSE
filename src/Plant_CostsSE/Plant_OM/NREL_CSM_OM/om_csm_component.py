"""
om_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from twister.components.varTrees import PlantOM

from twister.models.csm.csmOM import csmOM

class om_csm_component(Component):

    # ---- Design Variables --------------    

    # Turbine configuration
    # drivetrain
    ratedPower = Float(5000.0, units = 'kW', iotype = 'in', desc = 'rated power for a wind turbine')
    
    # Plant Configuration
    seaDepth = Float(20.0, units = 'm', iotype = 'in', desc = 'sea depth for offshore wind plant')
    year = Int(2009, units='yr', iotype='in', desc='year for project start')
    month = Int(12,  units='mon', iotype = 'in', desc= 'month for project start')
    turbineNumber = Int(100, iotype = 'in', desc = 'number of turbines at plant')
    aep = Float(1701626526.28, units = 'kW * h', iotype = 'in', desc = 'annual energy production for the plant')
        
    # ------------- Outputs --------------     

    OnMcost = Float(0.0, iotype='out', units='USD', desc='O&M costs') # kld - adding assembly output connections
    plantOM = VarTree(PlantOM(), iotype='out')
 
    def __init__(self):
        """
        OpenMDAO component to wrap O&M model of the NREL Cost and Scaling model data (csmOM.py).

        Parameters
        ----------
        ratedPower : float
          rated power for a wind turbine [kW]
        seaDepth : float
          sea depth for offshore wind plant [m]
        year : int
          year for project start
        month : int
          month for project start
        turbineNumber : int
          number of turbines at plant
        aep : float
          annual energy production for the plant [kWh]
        
        Returns
        -------
        OnMcost : float
          O&M costs [USD]
        plantOM : PlantOM
          Variable tree for detailed O&M outputs    
        """
        super(om_csm_component, self).__init__()

        #plant OM initiatlize
        self.add('plantOM', PlantOM())

        #initialize csmOM model
        self.csmOM = csmOM()

    def execute(self):
        """
        Execute the O&M Model of the NREL Cost and Scaling Model.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.aepTurbine = self.aep / self.turbineNumber
        self.csmOM.compute(self.aepTurbine, self.seaDepth, self.ratedPower, self.year, self.month)

        self.plantOM.preventativeMaintenanceCost = self.csmOM.getOMCost() * self.turbineNumber
        self.plantOM.correctiveMaintenanceCost = self.csmOM.getLRC() * self.turbineNumber
        self.plantOM.landLeaseCost = self.csmOM.getLLC() * self.turbineNumber
        self.plantOM.totalOMCost = self.plantOM.preventativeMaintenanceCost + self.plantOM.correctiveMaintenanceCost \
           + self.plantOM.landLeaseCost
        
        self.OnMcost = self.plantOM.totalOMCost


def example():

    # simple test of module

    om = om_csm_component()

    om.execute()
    print "OM onshore {:.1f}".format(om.plantOM.totalOMCost)
    print "OM by turbine {0}".format(om.plantOM.preventativeMaintenanceCost / om.turbineNumber)
    print "LRC by turbine {0}".format(om.plantOM.correctiveMaintenanceCost / om.turbineNumber)
    print "LLC by turbine {0}".format(om.plantOM.landLeaseCost / om.turbineNumber)
    
    om.seaDepth = 0.0
    om.execute()
    print "OM offshore {:.1f}".format(om.plantOM.totalOMCost)
    print "OM by turbine {0}".format(om.plantOM.preventativeMaintenanceCost / om.turbineNumber)
    print "LRC by turbine {0}".format(om.plantOM.correctiveMaintenanceCost / om.turbineNumber)
    print "LLC by turbine {0}".format(om.plantOM.landLeaseCost / om.turbineNumber)

if __name__ == "__main__":

    example()