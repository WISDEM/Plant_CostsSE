"""
bos_nrel_offshore_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, Int, VarTree, Str, Bool, Slot

from twister.fused_cost import GenericBOSCostModel

from twister.components.varTrees import PlantBOS

from twister.models.BOS.bos_nrel_XLS import bos_nrel_XLS
from twister.components.global_config import PlatformIsWindows

class bos_nrel_offshore_component(Component):
    """ Evaluates the NREL BOS spreadsheet """

    # ------------- Design Variables -----------------
    
    # Turbine Configuration
    # rotor
    ratedPower = Float(5000.0, units = 'kW', iotype='in', desc= 'rated machine power in kW')
    rotorDiameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine')
    bladeLength = Float(61.5, units = 'm', iotype='in', desc= 'length of a wind turbine blade')
    bladeWidth = Float(2.3, units = 'm', iotype='in', desc= 'width of blade at max chord position')
    hubDiameter = Float(3.0, units = 'm', iotype='in', desc = 'diameter of the hub')
    # drivetrain
    nacelleLength = Float(17.0, units = 'm', iotype='in', desc='length of the nacelle')
    nacelleHeight = Float(5.5, units = 'm', iotype = 'in', desc = 'height of the nacelle')
    nacelleWidth = Float(5.5, units = 'm', iotype = 'in', desc = 'width of the nacelle')
    # tower
    hubHeight = Float(90.0, units = 'm', iotype='in', desc = 'hub height for wind turbine')
    towerLength = Float(87.6, units = 'm', iotype = 'in', desc = 'length of tower')
    maxTowerDiameter = Float(6.0, units = 'm', iotype='in', desc = 'maximum diameter of the tower')
    # RNA
    RNAMass = Float(256634.5, units = 'kg', iotype='in', desc = 'mass of the rotor-nacelle assembly')
    
    # Plant Configuration
    seaDepth = Float(20.0, units = 'm', iotype='in', desc = 'sea depth for offshore wind project')
    distanceFromShore = Float(30.0, units = 'km', iotype='in', desc = 'distance of plant from shore')
    turbineNumber = Int(100, iotype='in', desc= 'number of turbines in plant')
    soilType = Str("Sand", iotype='in', desc = 'soil type at plant site')    

    # ------- Outputs ------------------  
    # while framework not working
    bos_cost = Float(0.0, iotype='out', units='USD', desc='Balance of station costs')       
    plantBOS = Slot(PlantBOS, iotype='out')

    def __init__(self):
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
        
        # initialize output variable tree
        self.add('plantBOS',PlantBOS())

        #open excel account
        self.bosnrelxls = bos_nrel_XLS(debug=False)
        if (PlatformIsWindows()):
            self.ssfile = 'C:/Python27/openmdao-0.7.0/twister/models/BOS/Offshore BOS Model.xlsx' # TODO: machine independence
        else:
            self.ssfile = "/Users/pgraf/work/wese/wese-6_13_12/twister/examples/excel_wrapper/bosMod.xlsx"
        self.bosnrelxls.ssopen(ssfile=self.ssfile)

        
    def execute(self):
        """
        Executes NREL BOS Offshore Excel model to estimate wind plant BOS costs.
        """
        print "In {0}.execute()...".format(self.__class__)

        # set input cells from user inputs and parameter scans
        self.bosnrelxls.setCell( 6,2,self.ratedPower*0.001) # spreadsheet uses MW        
        self.bosnrelxls.setCell( 7,2,self.turbineNumber)
        self.bosnrelxls.setCell( 8,2,self.seaDepth)
        self.bosnrelxls.setCell( 9,2,self.distanceFromShore)
        self.bosnrelxls.setCell(10,2,self.soilType)        
        self.bosnrelxls.setCell(11,2,self.rotorDiameter)
        self.bosnrelxls.setCell(12,2,self.hubHeight)


        #print [self.nacelleLength, self.nacelleHeight, self.nacelleWidth]
        #print [self.hubDiameter, self.bladeLength, self.bladeWidth]
        #print [self.towerLength, self.maxTowerDiameter]
        #print [self.RNAMass / 1000.0]

        # set input cells from other assemblies          
        self.bosnrelxls.setCell(23,2,self.nacelleLength)
        self.bosnrelxls.setCell(23,3,self.nacelleHeight) 
        self.bosnrelxls.setCell(23,4,self.nacelleWidth)
        self.bosnrelxls.setCell(23,5,self.hubDiameter)
        self.bosnrelxls.setCell(23,7,self.bladeLength)
        self.bosnrelxls.setCell(23,8,self.bladeWidth)
        self.bosnrelxls.setCell(23,9,self.towerLength)
        self.bosnrelxls.setCell(23,10,self.maxTowerDiameter)
        self.bosnrelxls.setCell(23,14,self.RNAMass / 1000.0) # input to spreadsheet is in tons
        
        # compute!!
        
        self.bos_cost      = self.bosnrelxls.getCell(3,2) * 1e6

        self.plantBOS.totalBOSCost = self.bos_cost
        self.plantBOS.foundationCost = self.bosnrelxls.getCell(10,2) * 1e3
        self.plantBOS.engineeringCost   = self.bosnrelxls.getCell(7,2) * 1e3
        self.plantBOS.permittingCost    = self.bosnrelxls.getCell(8,2) * 1e3
        self.plantBOS.developmentCost   = self.plantBOS.engineeringCost + self.plantBOS.permittingCost

        self.plantBOS.portsStagingCost    = self.bosnrelxls.getCell(9,2) * 1e3
        self.plantBOS.vesselsCost         = self.bosnrelxls.getCell(12,2) * 1e3
        self.plantBOS.assemblyInstallCost = self.plantBOS.vesselsCost

        self.plantBOS.electricalInterconnectCost = self.bosnrelxls.getCell(11,2) * 1e3

        self.plantBOS.offshoreDecommissioningCost = self.bosnrelxls.getCell(13,2) * 1e3
        self.plantBOS.offshoreAdditionalCost        = self.bosnrelxls.getCell(14,2) * 1e3
        self.plantBOS.offshoreInsuranceCost       = self.bosnrelxls.getCell(18,2) * 1e3
        self.plantBOS.offshoreContingenciesCost   = self.bosnrelxls.getCell(19,2) * 1e3
        
#----------------------------

def example():
  
    #TODO: adjust program main routines to be machine independent

    import time
    tt = time.time()    

    opt_problem = bos_nrel_offshore_component()
    opt_problem.execute()

    print "\n"
    print "Cost {:.3f} found at ({:.2f}) turbines".format(opt_problem.bos_cost, opt_problem.turbineNumber)
    print "plant BOS variable tree"
    opt_problem.plantBOS.printVT()

    opt_problem.bosnrelxls.ssclose()  

if __name__ == "__main__": # pragma: no cover    

    
    example()