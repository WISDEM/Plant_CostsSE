"""
om_ecn_offshore_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from gamma import gamma   # our own version
import numpy as np

from fusedwind.plant_cost.fused_costs_asym import ExtendedOPEXAggregator, ExtendedOPEXModel

from ecnomXLS import ecnomXLS

class om_ecn_assembly(ExtendedOPEXModel):
    
    # variables
    turbine_cost = Float(9000000.00, units='USD', iotype='in', desc = 'turbine system capital costs')
    machine_rating = Float(5000.0, units='kW', iotype='in', desc= 'wind turbine rated power')
    
    # parameters
    turbine_number = Int(100, iotype='in', desc = 'total number of wind turbines at the plant')
    project_lifetime = Float(20.0, iotype='in', desc = 'project lifetime for wind plant')
    
    # outputs
    availability  = Float(0.0, iotype='out', desc='Availability')

    def __init__(self, ssfile):
        
        self.ssfile = ssfile
      
        super(om_ecn_assembly, self).__init__()


    def configure(self):

        super(om_ecn_assembly,self).configure()
      
        self.replace('opex', om_ecn_offshore_component(self.ssfile))
        
        self.connect('turbine_cost','opex.turbine_cost')
        self.connect('machine_rating','opex.machine_rating')
        self.connect('turbine_number','opex.turbine_number')
        self.connect('project_lifetime','opex.project_lifetime')

        self.connect('opex.availability','availability')

class om_ecn_offshore_component(ExtendedOPEXAggregator):
    """ Evaluates the ECN O&M spreadsheet """

    # variables
    turbine_cost = Float(9000000.00, units='USD', iotype='in', desc = 'turbine system capital costs')
    machine_rating = Float(5000.0, units='kW', iotype='in', desc= 'wind turbine rated power')

    # parameters
    turbine_number = Int(100, iotype='in', desc = 'total number of wind turbines at the plant')
    project_lifetime = Float(20.0, iotype='in', desc = 'project lifetime for wind plant')

    # outputs
    availability  = Float(0.0, iotype='out', desc='Availability')

    def __init__(self, ssfile):
        """
        OpenMDAO component to wrap ECN Offshore O&M Excel Model (ecnomXLS.py).
        Call __init__ with a file name to override default ECN spreadsheet file

        Parameters
        ----------
        turbineCost : float
          turbine system capital costs per turbine [USD]
        machine_rating : float
          rated power for a wind turbine [kW]
        turbine_number : int
          number of turbines at plant
        project_lifetime : float
          project liftime for wind plant
        
        Returns
        -------
        plantOM : PlantOM
          Variable tree for detailed O&M outputs    
        availability : float
          availability for wind plant
        """
        
        super(om_ecn_offshore_component, self).__init__()

        #open excel account
        self.ecnxls = ecnomXLS(debug=False)
        self.ecnxls.ssopen(ssfile)

    def execute(self):
        """
        Executes the ECN O&M Offshore model using excel spreadsheet and finds total and detailed O&M costs for the plant as well as availability.
        """
        print "In {0}.execute()...".format(self.__class__)

        # Inputs - copy to spreadsheet

        # set basic plant inputs        
        self.ecnxls.setCell( 6,3,self.turbine_number)
        self.ecnxls.setCell( 5,8,self.machine_rating)
        self.ecnxls.setCell( 7,3,self.project_lifetime)

        # set basic turbine inputs
        self.invCosts = self.turbine_cost / self.machine_rating  # investment costs per kW
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
        self.OPEX_breakdown.lease_opex = 21.0 * self.turbine_number * self.machine_rating # hack to include land lease costs not in ECN model, cost from COE Review 2011
        self.avg_annual_opex += self.OPEX_breakdown.lease_opex

        self.OPEX_breakdown.corrective_opex = self.ecnxls.getCell(51,9) * 1000 + self.ecnxls.getCell(52,9) * 1000
        self.OPEX_breakdown.preventative_opex = self.ecnxls.getCell(53,9) * 1000
        self.OPEX_breakdown.other_opex    = self.ecnxls.getCell(54,9) * 1000
        
    def close(self):
        """
        Close the spreadsheet inputs and clean up
        """
        self.ecnxls.ssclose()

#----------------------------

def example(ssfile):
             
    om = om_ecn_assembly(ssfile)
    om.machine_rating = 5000.0
    om.turbine_cost = 9000000.0
    om.turbine_number = 100
    om.project_lifetime = 20
    
    om.run()

    print "Availability {:.1f}% ".format(om.availability*100.0)
    print "OnM Annual Costs ${:.3f} ".format(om.avg_annual_opex)
    print "OM by turbine {0}".format(om.OPEX_breakdown.preventative_opex / om.turbine_number)
    print "LRC by turbine {0}".format(om.OPEX_breakdown.corrective_opex / om.turbine_number)
    print "LLC by turbine {0}".format(om.OPEX_breakdown.lease_opex / om.turbine_number)

if __name__ == "__main__": # pragma: no cover         

    ssfile = 'C:/Models/ECN Model/ECN O&M Model.xls'

    example(ssfile)