"""
bos_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from twister.components.varTrees import PlantBOS

from twister.models.csm.csmBOS import csmBOS

class bos_csm_component(Component):

    # ---- Design Variables --------------    

    # Turbine configuration
    # rotor
    rotorDiameter = Float(126.0, units = 'm', iotype = 'in', desc = 'rotor diameter for wind turbine')
    # drivetrain
    ratedPower = Float(5000.0, units = 'kW', iotype = 'in', desc = 'rated power for a wind turbine')
    # tower
    hubHeight = Float(90.0, units = 'm', iotype = 'in', desc = 'hub height for wind turbine')
    
    # Plant Configuration
    seaDepth = Float(20.0, units = 'm', iotype = 'in', desc = 'sea depth for offshore wind plant')
    turbineCost = Float(9000000.00, units='USD', iotype='in', desc='Turbine capital costs')
    year = Int(2009, units='yr', iotype='in', desc='year for project start')
    month = Int(12,  units='mon', iotype = 'in', desc= 'month for project start')
    turbineNumber = Int(100, iotype = 'in', desc = 'number of turbines at plant')
        
    # ------------- Outputs --------------     
  
    BOScost = Float(0.0, iotype='out', units='USD', desc='Balance of station total costs excluding foundation')
    plantBOS = VarTree(PlantBOS(),iotype='out')


    def __init__(self):
        """
        OpenMDAO component to wrap BOS model of the NREL Cost and Scaling Model (csmBOS.py)
        
        Parameters
        ----------
        rotorDiameter : float
          rotor diameter of the machine [m]
        ratedPower : float
          rated power for a wind turbine [kW]
        hubHeight : float
          hub height for wind turbine [m]
        seaDepth : float
          sea depth for offshore wind plant [m]
        turbineCost : float
          Turbine capital costs per turbine [USD]
        year : int
          year of project start
        month : int
          month of project start
        turbineNumber : int
          number of turbines at plant
          
        Returns
        -------
        BOSCost : float
          Balance of station total costs excluding foundation
        plantBOS : PlantBOS
          Variable tree container for detailed BOS cost breakdown based on NREL Offshore Cost Breakdown Structure
        
        """
        super(bos_csm_component, self).__init__()
        
        # initialize output variable tree
        self.add('plantBOS',PlantBOS())

        #initialize csmBOS model
        self.csmBOS   = csmBOS()

    def execute(self):
        """
        Executes BOS model of the NREL Cost and Scaling Model to estimate wind plant BOS costs.
        """


        print "In {0}.execute()...".format(self.__class__)

        self.csmBOS.compute(self.seaDepth,self.ratedPower,self.hubHeight,self.rotorDiameter, self.turbineCost, self.year, self.month)

        self.BOScost = self.csmBOS.getCost() * self.turbineNumber

        [self.plantBOS.foundationCost, self.plantBOS.landTransportationCost, self.plantBOS.landCivilCost, self.plantBOS.portsStagingCost, \
         self.plantBOS.installationCost, self.plantBOS.electricalInterconnectCost, self.plantBOS.developmentCost, \
         self.accessEquipmentCost, self.scourCost, self.plantBOS.offshoreAdditionalCost] = \
                      self.csmBOS.getDetailedCosts()

        [self.plantBOS.foundationCost, self.plantBOS.landTransportationCost, self.plantBOS.landCivilCost, self.plantBOS.portsStagingCost, \
         self.plantBOS.installationCost, self.plantBOS.electricalInterconnectCost, self.plantBOS.developmentCost, \
         self.accessEquipmentCost, self.scourCost, self.plantBOS.offshoreAdditionalCost] = \
                        [self.plantBOS.foundationCost * self.turbineNumber, self.plantBOS.landTransportationCost * self.turbineNumber, \
                         self.plantBOS.landCivilCost * self.turbineNumber, \
                         self.plantBOS.portsStagingCost * self.turbineNumber, self.plantBOS.installationCost * self.turbineNumber, \
                         self.plantBOS.electricalInterconnectCost * self.turbineNumber, self.plantBOS.developmentCost * self.turbineNumber, \
                         self.accessEquipmentCost * self.turbineNumber, self.scourCost * self.turbineNumber, \
                         self.plantBOS.offshoreAdditionalCost * self.turbineNumber] 
        
        self.plantBOS.offshoreOtherCost = self.accessEquipmentCost + self.scourCost
        self.plantBOS.assemblyInstallationCost = self.plantBOS.installationCost
    

def example():
	
	  # simple test of module
    bos = bos_csm_component()
    bos.execute()
    print "BOS cost offshore: {0}".format(bos.BOScost)
    print "BOS cost per turbine: {0}".format(bos.BOScost / bos.turbineNumber)
    print "Plant BOS variable tree"
    bos.plantBOS.printVT()
    
    bos.seaDepth = 0.0
    bos.turbineCost = 5229222.77
    bos.execute()
    print "BOS cost onshore: {0}".format(bos.BOScost)
    print "BOS cost per turbine: {0}".format(bos.BOScost / bos.turbineNumber)
    print "Plant BOS variable tree"
    bos.plantBOS.printVT()

if __name__ == "__main__":

    example()