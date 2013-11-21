"""
bos_nrel_offshore_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Str, Array, VarTree

from fusedwind.plant_cost.fused_costs_asym import BOSVarTree, ExtendedBOSCostAggregator, ExtendedBOSCostModel

from bos_nrel_XLS import bos_nrel_XLS
from foundation_costSE import foundation_mc_component

class bos_nrel_offshore_assembly(ExtendedBOSCostModel):

    sea_depth = Float(20.0, units = 'm', iotype='in', desc = 'project site water depth')
    
    def __init__(self, ssfile):

        self.ssfile = ssfile
    
        super(bos_nrel_offshore_assembly, self).__init__()

    def configure(self):

        super(bos_nrel_offshore_assembly, self).configure()
    
        self.replace('bos', bos_nrel_offshore_component(self.ssfile))
        self.add('foundation', foundation_mc_component())
        
        self.driver.workflow.add('foundation')

        self.connect('sea_depth', ['bos.seaDepth', 'foundation.seaDepth'])
        self.create_passthrough('bos.bladeLength')
        self.create_passthrough('bos.bladeWidth')
        self.create_passthrough('bos.hubDiameter')
        self.create_passthrough('bos.nacelleLength')
        self.create_passthrough('bos.nacelleHeight')
        self.create_passthrough('bos.nacelleWidth')
        self.create_passthrough('bos.towerLength')
        self.create_passthrough('bos.maxTowerDiameter')
        self.create_passthrough('bos.distanceFromShore')
        self.create_passthrough('bos.soilType')

        self.create_passthrough('foundation.monopileMass')
        self.create_passthrough('foundation.transitionMass')
        self.connect('machine_rating', 'foundation.ratedPower')
        
        self.connect('foundation.foundation_cost', 'bos.foundation_cost')

class bos_nrel_offshore_component(ExtendedBOSCostAggregator):
    """ Evaluates the NREL BOS spreadsheet """

    # variables
    bladeLength = Float(61.5, units = 'm', iotype='in', desc= 'length of a wind turbine blade')
    bladeWidth = Float(2.3, units = 'm', iotype='in', desc= 'width of blade at max chord position')
    hubDiameter = Float(3.0, units = 'm', iotype='in', desc = 'diameter of the hub')
    nacelleLength = Float(17.0, units = 'm', iotype='in', desc='length of the nacelle')
    nacelleHeight = Float(5.5, units = 'm', iotype = 'in', desc = 'height of the nacelle')
    nacelleWidth = Float(5.5, units = 'm', iotype = 'in', desc = 'width of the nacelle')
    towerLength = Float(87.6, units = 'm', iotype = 'in', desc = 'length of tower')
    maxTowerDiameter = Float(6.0, units = 'm', iotype='in', desc = 'maximum diameter of the tower')
    seaDepth = Float(20.0, units = 'm', iotype='in', desc = 'sea depth for offshore wind project')
    foundation_cost = Float(0.0, units='USD', iotype='in', desc='cost for a foundation')

    # parameters
    distanceFromShore = Float(30.0, units = 'km', iotype='in', desc = 'distance of plant from shore')
    soilType = Str("Sand", iotype='in', desc = 'soil type at plant site')    

    def __init__(self, ssfile):
        """
        OpenMDAO component to wrap NREL Offshore BOS Excel Model (bos_nrel_XLS.py)
        
        Parameters
        ----------
        ratedPower : float
          rated power for a wind turbine [kW]
        rotorDiameter : float
          rotor diameter of the machine [m]
        bladeLength : float
          length of a wind turbine blade [m]
        bladeWidth : float
          width of blade at max chord position [m]
        hubDiameter : float
          diameter of the hub [m]
        nacelleLength : float
          length of the nacelle [m]
        nacelleHeight : float
          height of the nacelle [m]
        nacelleWidth : float
          width of the nacelle [m]
        hubHeight : float
          hub height for wind turbine [m]
        towerLength : float
          length of tower [m]
        maxTowerDiameter : float
          maximum diameter of the tower [m]
        RNAMass : float
          mass of the rotor-nacelle assembly [kg]
        seaDepth : float
          sea depth for offshore wind project [m]
        distanceFromShore : float
          distance of plant from shore [m]
        turbineNumber : int
          number of turbines in plant
        soilType : str
          soil type at plant site - Sand only option at present
          
        Returns
        -------
        bos_cost : float
          Balance of station total costs excluding foundation
        plantBOS : PlantBOS
          Variable tree container for detailed BOS cost breakdown based on NREL Offshore Cost Breakdown Structure
        
        """
        
        super(bos_nrel_offshore_component, self).__init__()

        #open excel account
        self.bosnrelxls = bos_nrel_XLS(debug=False)
        print ssfile
        self.bosnrelxls.ssopen(ssfile)
        
    def execute(self):
        """
        Executes NREL BOS Offshore Excel model to estimate wind plant BOS costs.
        """
        print "In {0}.execute()...".format(self.__class__)

        # set input cells from user inputs and parameter scans
        self.bosnrelxls.setCell( 6,2,self.machine_rating*0.001) # spreadsheet uses MW        
        self.bosnrelxls.setCell( 7,2,self.turbine_number)
        self.bosnrelxls.setCell( 8,2,self.seaDepth)
        self.bosnrelxls.setCell( 9,2,self.distanceFromShore)
        self.bosnrelxls.setCell(10,2,self.soilType)        
        self.bosnrelxls.setCell(11,2,self.rotor_diameter)
        self.bosnrelxls.setCell(12,2,self.hub_height)

        # set input cells from other assemblies          
        self.bosnrelxls.setCell(23,2,self.nacelleLength)
        self.bosnrelxls.setCell(23,3,self.nacelleHeight) 
        self.bosnrelxls.setCell(23,4,self.nacelleWidth)
        self.bosnrelxls.setCell(23,5,self.hubDiameter)
        self.bosnrelxls.setCell(23,7,self.bladeLength)
        self.bosnrelxls.setCell(23,8,self.bladeWidth)
        self.bosnrelxls.setCell(23,9,self.towerLength)
        self.bosnrelxls.setCell(23,10,self.maxTowerDiameter)
        self.bosnrelxls.setCell(23,14,self.RNA_mass / 1000.0) # input to spreadsheet is in tons
        
        # compute!!

        self.bos_costs      = self.bosnrelxls.getCell(3,2) * 1e6 - self.bosnrelxls.getCell(10,2) * 1e3 + self.foundation_cost * self.turbine_number

        self.BOS_breakdown.development_costs = self.bosnrelxls.getCell(7,2) * 1e3 + self.bosnrelxls.getCell(8,2) * 1e3
        self.BOS_breakdown.preparation_and_staging_costs = self.bosnrelxls.getCell(9,2) * 1e3 
        self.BOS_breakdown.transportation_costs = 0.0
        self.BOS_breakdown.foundation_and_substructure_costs = self.foundation_cost
        self.BOS_breakdown.electrical_costs = self.bosnrelxls.getCell(11,2) * 1e3
        self.BOS_breakdown.assembly_and_installation_costs = self.bosnrelxls.getCell(12,2) * 1e3 #TODO: vessels?
        self.BOS_breakdown.soft_costs = self.bosnrelxls.getCell(18,2) * 1e3 + self.bosnrelxls.getCell(19,2) * 1e3 + \
                                        self.bosnrelxls.getCell(13,2) * 1e3 + self.bosnrelxls.getCell(14,2) * 1e3
        self.BOS_breakdown.other_costs = 0.0
        
#----------------------------

def example(ssfile):  

    bos = bos_nrel_offshore_assembly(ssfile)
    bos.machine_rating = 5000.0
    bos.rotor_diameter = 126.0
    bos.turbine_cost = 5950209.283
    bos.turbine_number = 100
    bos.hub_height = 90.0
    bos.RNA_mass = 256634.5

    bos.execute()

    print "Cost {:.3f} found at ({:.2f}) turbines".format(bos.bos_costs, bos.turbine_number)

    bos.bos.bosnrelxls.ssclose()  

if __name__ == "__main__": # pragma: no cover    

    ssfile = 'C:/Models/BOS/Offshore BOS Model.xlsx'
    
    example(ssfile)