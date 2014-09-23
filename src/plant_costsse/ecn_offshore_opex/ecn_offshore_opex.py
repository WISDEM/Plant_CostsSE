"""
om_ecn_offshore_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

import numpy as np

from fusedwind.plant_cost.fused_opex import OPEXVarTree, ExtendedOPEXAggregator, ExtendedOPEXModel, configure_extended_opex
from fusedwind.interface import implement_base

from ecnomXLS import ecnomXLS

@implement_base(ExtendedOPEXModel)
class opex_ecn_assembly(Assembly):

    # variables
    turbine_cost = Float(units='USD', iotype='in', desc = 'turbine system capital costs')
    machine_rating = Float(units='kW', iotype='in', desc= 'wind turbine rated power')

    # parameters
    turbine_number = Int(100, iotype='in', desc = 'total number of wind turbines at the plant')
    project_lifetime = Float(20.0, iotype='in', desc = 'project lifetime for wind plant')

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')
    opex_breakdown = VarTree(OPEXVarTree(),iotype='out')
    availability  = Float(0.0, iotype='out', desc='Availability')

    def __init__(self, ssfile=None):
        
        self.ssfile = ssfile
      
        Assembly.__init__(self)

    def configure(self):

        configure_extended_opex(self)
      
        self.replace('opex', opex_ecn_offshore_component(self.ssfile))
        
        self.connect('turbine_cost','opex.turbine_cost')
        self.connect('machine_rating','opex.machine_rating')
        self.connect('turbine_number','opex.turbine_number')
        self.connect('project_lifetime','opex.project_lifetime')

        self.connect('opex.availability','availability')

@implement_base(ExtendedOPEXAggregator)
class opex_ecn_offshore_component(Component):
    """ Evaluates the ECN O&M spreadsheet """

    # variables
    turbine_cost = Float(units='USD', iotype='in', desc = 'turbine system capital costs')
    machine_rating = Float(units='kW', iotype='in', desc= 'wind turbine rated power')

    # parameters
    turbine_number = Int(100, iotype='in', desc = 'total number of wind turbines at the plant')
    project_lifetime = Float(20.0, iotype='in', desc = 'project lifetime for wind plant')

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')
    opex_breakdown = VarTree(OPEXVarTree(),iotype='out')
    availability  = Float(0.0, iotype='out', desc='Availability')

    def __init__(self, ssfile=None):
        """
        OpenMDAO component to wrap ECN Offshore O&M Excel Model (ecnomXLS.py).
        Call __init__ with a file name to override default ECN spreadsheet file
        """
        
        Component.__init__(self)

        #open excel account
        self.ecnxls = ecnomXLS(debug=False)
        self.ecnxls.ssopen(ssfile)

    def execute(self):
        """
        Executes the ECN O&M Offshore model using excel spreadsheet and finds total and detailed O&M costs for the plant as well as availability.
        """
        # print "In {0}.execute()...".format(self.__class__)

        # Inputs - copy to spreadsheet

        # set basic plant inputs        
        self.ecnxls.setCell( 6,3,self.turbine_number)
        self.ecnxls.setCell( 5,8,self.machine_rating)
        self.ecnxls.setCell( 7,3,self.project_lifetime)

        # set basic turbine inputs
        self.invCosts = self.turbine_cost / self.machine_rating  # investment costs per kW
        self.ecnxls.setCell( 6,8,self.invCosts)
        
        # Outputs - read from spreadsheet

        self.availability = self.ecnxls.getCell(20,9)
        self.avg_annual_opex      = self.ecnxls.getCell(56,9) * 1000
        self.opex_breakdown.lease_opex = 21.0 * self.turbine_number * self.machine_rating # hack to include land lease costs not in ECN model, cost from COE Review 2011
        self.avg_annual_opex += self.opex_breakdown.lease_opex

        self.opex_breakdown.corrective_opex = self.ecnxls.getCell(51,9) * 1000 + self.ecnxls.getCell(52,9) * 1000
        self.opex_breakdown.preventative_opex = self.ecnxls.getCell(53,9) * 1000
        self.opex_breakdown.other_opex    = self.ecnxls.getCell(54,9) * 1000
        
    def close(self):
        """
        Close the spreadsheet inputs and clean up
        """
        self.ecnxls.ssclose()

#----------------------------

def example(ssfile):
             
    om = opex_ecn_assembly(ssfile)
    om.machine_rating = 5000.0
    om.turbine_cost = 9000000.0
    om.turbine_number = 100
    om.project_lifetime = 20
    
    om.run()

    print "Average annual operational expenditures for an offshore wind plant with 100 NREL 5 MW turbines"
    print "OPEX offshore ${:.2f} USD".format(om.avg_annual_opex)
    print "Preventative OPEX by turbine ${:.2f} USD".format(om.opex_breakdown.preventative_opex / om.turbine_number)
    print "Corrective OPEX by turbine ${:.2f} USD".format(om.opex_breakdown.corrective_opex / om.turbine_number)
    print "Land Lease OPEX by turbine ${:.2f} USD".format(om.opex_breakdown.lease_opex / om.turbine_number)
    print "and plant availability of {:.1f}% ".format(om.availability*100.0)
    print

if __name__ == "__main__": # pragma: no cover         

    ssfile = 'C:/Models/ECN Model/ECN O&M Model.xls'

    example(ssfile)