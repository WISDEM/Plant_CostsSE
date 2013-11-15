"""
om_ecn_offshore_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree, Slot

from twister.fused_cost import GenericOPEXModel

from twister.components.varTrees import PlantOM

from twister.models.OM.ECN.ecnomXLS import ecnomXLS
from twister.components.global_config import PlatformIsWindows

from gamma import gamma   # our own version
import numpy as np

class om_ecn_offshore_component(Component):
    """ Evaluates the ECN O&M spreadsheet """

    # --------- Design Variables ------------

    #Turbine configuration
    turbineCost = Float(9000000.00, units='USD', iotype='in', desc = 'turbine system capital costs')
    ratedPower = Float(5000.0, units='kW', iotype='in', desc= 'wind turbine rated power')
    """    hubHeight = Float(90.0, units = 'm', iotype='in', desc='hub height of wind turbine above ground / sea level')
    powerCurve = Array(np.array([[0.0,0.0],[25.0,0.0]]),iotype='in', desc= 'turbine power curve [kw] as a function of wind speed [m/s]')"""
    
    #Plant configuration
    turbineNumber = Int(100, iotype='in', desc = 'total number of wind turbines at the plant')
    projectLifetime = Float(20.0, iotype='in', desc = 'project lifetime for wind plant')
    """    shearExponent = Float(0.143, iotype='in', desc= 'shear exponent for wind plant')
    windSpeed50m = Float(8.25, units = 'm/s', iotype='in', desc='mean annual wind speed at 50 m height')
    weibullK= Float(2.4, iotype='in', desc = 'weibull shape factor for annual wind speed distribution')
    soilingLosses = Float(0.0, iotype='in', desc = 'energy losses due to blade soiling for the wind plant - average across turbines')
    arrayLosses = Float(0.10, iotype='in', desc = 'energy losses due to turbine interactions - across entire plant')"""

    # ------------- Outputs --------------   

    plantOM = Slot(PlantOM, iotype='out')
    availability  = Float(0.0, iotype='out', desc='Availability')
    # while framework not working
    avg_annual_opex = Float(0.0, iotype='out', units='USD', desc='average annual opex')

    def __init__(self, ssfile=None):
        """
        OpenMDAO component to wrap ECN Offshore O&M Excel Model (ecnomXLS.py).
        Call __init__ with a file name to override default ECN spreadsheet file

        Parameters
        ----------
        turbineCost : float
          turbine system capital costs per turbine [USD]
        ratedPower : float
          rated power for a wind turbine [kW]
        turbineNumber : int
          number of turbines at plant
        projectLifetime : float
          project liftime for wind plant
        
        Returns
        -------
        plantOM : PlantOM
          Variable tree for detailed O&M outputs    
        availability : float
          availability for wind plant
        """
        
        super(om_ecn_offshore_component, self).__init__()

        # plant OM variable tree
        self.add('plantOM',PlantOM())

        #open excel account
        self.ecnxls = ecnomXLS(debug=False)
        if (PlatformIsWindows()):
            self.ssfile = 'C:/Python27/openmdao-0.7.0/twister/models/OM/ECN/ECN O&M Model.xls' # TODO: machine independence
            #self.ssfile  = r'Y:/win/wese/wese-9_6_12/twister/models/BOS/Offshore BOS model 12-8-7.xlsx'
        else:
            self.ssfile = "/Users/pgraf/work/wese/wese-6_13_12/twister/examples/excel_wrapper/bosMod.xlsx"
        self.ecnxls.ssopen(self.ssfile)

    def execute(self):
        """
        Executes the ECN O&M Offshore model using excel spreadsheet and finds total and detailed O&M costs for the plant as well as availability.
        """
        print "In {0}.execute()...".format(self.__class__)

        # Inputs - copy to spreadsheet

        # set basic plant inputs        
        self.ecnxls.setCell( 6,3,self.turbineNumber)
        self.ecnxls.setCell( 5,8,self.ratedPower)
        self.ecnxls.setCell( 7,3,self.projectLifetime)

        # set basic turbine inputs
        self.invCosts = self.turbineCost / self.ratedPower  # investment costs per kW
        self.ecnxls.setCell( 6,8,self.invCosts)

        """     
        # Unnecessary - only used for AEP calculations which are not being done here
        
        # set turbine parameters
        self.ecnxls.setCell(31,3,self.hubHeight)
        self.windFarmEfficiency = (1.0 - self.arrayLosses) * (1.0 - self.soilingLosses)
        self.ecnxls.setCell(34,3,self.windFarmEfficiency)

        # set wind climate parameters
        self.weibullL = self.windSpeed50m / np.exp(np.log(gamma(1.+1./self.weibullK)))
        for irow in range(39,44):
            self.ecnxls.setCell(irow,3,self.weibullK)
            self.ecnxls.setCell(irow,4,self.weibullL)  
        
        self.windDataHeight = 50
        self.ecnxls.setCell(37,4,self.windDataHeight)
        self.ecnxls.setCell(38,9,self.shearExponent)

        # input power curve        
        windSpeed = 3
        irow = 48
        for i in xrange(0,self.powerCurve.shape[1]):
           X = self.powerCurve[0,i]
           if (windSpeed == X) and (windSpeed <= 33):
             self.ecnxls.setCell(irow,4,self.powerCurve[1,i])
             windSpeed +=1
             irow += 1

        # set capacity factor based on power curve results # todo: need to get from correct sheet
        self.capFactor = self.ecnxls.getInputCell(27,3)
        print self.capFactor
        for irow in range(12,17):
            self.ecnxls.setCell(irow,3,self.capFactor)"""
        
        # Outputs - read from spreadsheet

        self.availability = self.ecnxls.getCell(20,9)
        self.avg_annual_opex      = self.ecnxls.getCell(56,9) * 1000
        self.plantOM.landLeaseCost = 21.0 * self.turbineNumber * self.ratedPower # hack to include land lease costs not in ECN model, cost from COE Review 2011
        self.avg_annual_opex += self.plantOM.landLeaseCost
        self.plantOM.totalOMCost = self.avg_annual_opex
        self.plantOM.correctiveTurbineMaintenanceCost   = self.ecnxls.getCell(51,9) * 1000
        self.plantOM.correctiveBOPMaintenanceCost  = self.ecnxls.getCell(52,9) * 1000
        self.plantOM.correctiveMaintenanceCost = self.plantOM.correctiveTurbineMaintenanceCost + self.plantOM.correctiveBOPMaintenanceCost
        self.plantOM.preventativeMaintenanceCost     = self.ecnxls.getCell(53,9) * 1000
        self.plantOM.fixedOMCost    = self.ecnxls.getCell(54,9) * 1000
        
    def close(self):
        """
        Close the spreadsheet inputs and clean up
        """
        self.ecnxls.ssclose()

#----------------------------

def example():

    import time
             
    ssfile = r'C:/Python27/openmdao-0.7.0/twister/models/OM/ECN/ECN O&M Model.xls'  # TODO : fix machine dependence
    opt_problem = om_ecn_offshore_component(ssfile=ssfile)
    
    tt = time.time()
    
    """    opt_problem.powerCurve = [[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, \
                           11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0], \
                          [0.0, 0.0, 0.0, 0.0, 187.0, 350.0, 658.30, 1087.4, 1658.3, 2391.5, 3307.0, \
                          4415.70, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, 5000.0, \
                          5000.0, 5000.0, 5000.0, 5000.0, 0.0]]"""
    
    opt_problem.execute()
    
    #opt_problem.close() # close the Excel spreadsheet

    print "Availability {:.1f}% ".format(opt_problem.availability*100.0)
    print "OnM Annual Costs ${:.3f} ".format(opt_problem.avg_annual_opex)
    print "O&M variable tree:"
    opt_problem.plantOM.printVT()

    print "Elapsed time: {:.3f} seconds".format(time.time()-tt)

if __name__ == "__main__": # pragma: no cover         


    example()