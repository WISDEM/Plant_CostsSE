"""
om_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from fusedwind.plant_cost.fused_opex import OPEXVarTree, ExtendedOPEXAggregator, ExtendedOPEXModel, configure_extended_opex
from fusedwind.interface import implement_base

from commonse.config import *
import numpy as np

@implement_base(ExtendedOPEXModel)
class opex_csm_assembly(Assembly):

    # variables
    machine_rating = Float(5000.0, units = 'kW', iotype = 'in', desc = 'rated power for a wind turbine')
    net_aep = Float(1701626526.28, units = 'kW * h', iotype = 'in', desc = 'annual energy production for the plant')

    # parameters
    sea_depth = Float(20.0, units = 'm', iotype = 'in', desc = 'sea depth for offshore wind plant')
    year = Int(2009, units='yr', iotype='in', desc='year for project start')
    month = Int(12, iotype = 'in', desc= 'month for project start') # units = months
    turbine_number = Int(100, iotype = 'in', desc = 'number of turbines at plant')

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')
    opex_breakdown = VarTree(OPEXVarTree(),iotype='out')

    def configure(self):

        super(opex_csm_assembly,self).configure()
        
        configure_extended_opex(self)

        self.replace('opex', opex_csm_component())

        self.connect('machine_rating','opex.machine_rating')
        self.connect('sea_depth','opex.sea_depth')
        self.connect('net_aep','opex.net_aep')
        self.connect('year','opex.year')
        self.connect('month','opex.month')
        self.connect('turbine_number','opex.turbine_number')

@implement_base(ExtendedOPEXAggregator)
class opex_csm_component(Component):

    # variables
    machine_rating = Float(5000.0, units = 'kW', iotype = 'in', desc = 'rated power for a wind turbine')
    net_aep = Float(1701626526.28, units = 'kW * h', iotype = 'in', desc = 'annual energy production for the plant')

    # parameters
    sea_depth = Float(20.0, units = 'm', iotype = 'in', desc = 'sea depth for offshore wind plant')
    year = Int(2009, units='yr', iotype='in', desc='year for project start')
    month = Int(12, iotype = 'in', desc= 'month for project start') # units = months
    turbine_number = Int(100, iotype = 'in', desc = 'number of turbines at plant')

    # Outputs
    avg_annual_opex = Float(iotype='out', desc='Average annual Operating Expenditures for a wind plant over its lifetime')
    opex_breakdown = VarTree(OPEXVarTree(),iotype='out')

    def __init__(self):
        """
        OpenMDAO component to wrap O&M model of the NREL _cost and Scaling model data (csmOM.py).

        """
        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
        """
        Execute the O&M Model of the NREL _cost and Scaling Model.
        """
        # print "In {0}.execute()...".format(self.__class__)

        # initialize variables
        if self.sea_depth == 0:
            offshore = False
        else:
            offshore = True
        ppi.curr_yr = self.year
        ppi.curr_mon = self.month

        #O&M
        offshoreCostFactor = 0.0200  # $/kwH
        landCostFactor     = 0.0070  # $/kwH
        if not offshore:  # kld - place for an error check - iShore should be in 1:4
            cost = self.net_aep * landCostFactor
            costEscalator = ppi.compute('IPPI_LOM')
        else:
            cost = self.net_aep * offshoreCostFactor
            ppi.ref_yr = 2003
            costEscalator = ppi.compute('IPPI_OOM')
            ppi.ref_yr = 2002

        self.opex_breakdown.preventative_opex = cost * costEscalator # in $/year

        #LRC
        if not offshore:
            lrcCF = 10.70 # land based
            costlrcEscFactor = ppi.compute('IPPI_LLR')
        else: #TODO: transition and deep water options if applicable
            lrcCF = 17.00 # offshore
            ppi.ref_yr = 2003
            costlrcEscFactor = ppi.compute('IPPI_OLR')
            ppi.ref_yr = 2002

        self.opex_breakdown.corrective_opex = self.machine_rating * lrcCF * costlrcEscFactor * self.turbine_number # in $/yr

        #LLC
        if not offshore:
            leaseCF = 0.00108 # land based
            costlandEscFactor = ppi.compute('IPPI_LSE')
        else: #TODO: transition and deep water options if applicable
            leaseCF = 0.00108 # offshore
            costlandEscFactor = ppi.compute('IPPI_LSE')

        self.opex_breakdown.lease_opex = self.net_aep * leaseCF * costlandEscFactor # in $/yr

        #Other
        self.opex_breakdown.other_opex = 0.0

        #Total OPEX
        self.avg_annual_opex = self.opex_breakdown.preventative_opex + self.opex_breakdown.corrective_opex \
           + self.opex_breakdown.lease_opex


        #dervivatives
        self.d_corrective_d_aep = 0.0
        self.d_corrective_d_rating = lrcCF * costlrcEscFactor * self.turbine_number
        self.d_lease_d_aep = leaseCF * costlandEscFactor
        self.d_lease_d_rating = 0.0
        self.d_other_d_aep = 0.0
        self.d_other_d_rating = 0.0
        if not offshore:
            self.d_preventative_d_aep = landCostFactor * costEscalator
        else:
            self.d_preventative_d_aep = offshoreCostFactor * costEscalator
        self.d_preventative_d_rating = 0.0
        self.d_opex_d_aep = self.d_preventative_d_aep + self.d_corrective_d_aep + self.d_lease_d_aep + self.d_other_d_aep
        self.d_opex_d_rating = self.d_preventative_d_rating + self.d_corrective_d_rating + self.d_lease_d_rating + self.d_other_d_rating

    def list_deriv_vars(self):


        inputs = ['net_aep', 'machine_rating']
        outputs = ['opex_breakdown.preventative_opex', 'opex_breakdown.corrective_opex', 'opex_breakdown.lease_opex', \
                  'opex_breakdown.other_opex', 'avg_annual_opex']

        return inputs, outputs

    def provideJ(self):

        self.J = np.array([[self.d_preventative_d_aep, self.d_preventative_d_rating], [self.d_corrective_d_aep, self.d_corrective_d_rating],\
                           [self.d_lease_d_aep, self.d_lease_d_rating], [self.d_other_d_aep, self.d_other_d_rating],\
                           [self.d_opex_d_aep, self.d_opex_d_rating]])

        return self.J


def example():

    # simple test of module

    om = opex_csm_assembly()

    om.machine_rating = 5000.0 # Need to manipulate input or underlying component will not execute
    om.net_aep = 1701626526.28
    om.sea_depth = 20.0
    om.year = 2010
    om.month = 12
    om.turbine_number = 100

    om.run()
    print "OM offshore {:.1f}".format(om.avg_annual_opex)
    print "OM by turbine {0}".format(om.opex_breakdown.preventative_opex / om.turbine_number)
    print "LRC by turbine {0}".format(om.opex_breakdown.corrective_opex / om.turbine_number)
    print "LLC by turbine {0}".format(om.opex_breakdown.lease_opex / om.turbine_number)
    print

    om.sea_depth = 0.0
    om.run()
    print "OM onshore {:.1f}".format(om.avg_annual_opex)
    print "OM by turbine {0}".format(om.opex_breakdown.preventative_opex / om.turbine_number)
    print "LRC by turbine {0}".format(om.opex_breakdown.corrective_opex / om.turbine_number)
    print "LLC by turbine {0}".format(om.opex_breakdown.lease_opex / om.turbine_number)

if __name__ == "__main__":

    example()