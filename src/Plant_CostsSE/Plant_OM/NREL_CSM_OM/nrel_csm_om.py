"""
om_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from fusedwind.plant_cost.fused_costs_asym import OPEXVarTree, ExtendedOPEXAggregator, ExtendedOPEXModel

from commonse.config import *
import numpy as np

class om_csm_assembly(ExtendedOPEXModel):

    def configure(self):

        super(om_csm_assembly,self).configure()
      
        self.replace('opex', om_csm_component())
        
        self.create_passthrough('opex.machine_rating')
        self.create_passthrough('opex.sea_depth')
        self.create_passthrough('opex.net_aep')
        self.create_passthrough('opex.year')
        self.create_passthrough('opex.month')
        self.create_passthrough('opex.turbine_number')

class om_csm_component(ExtendedOPEXAggregator):

    # variables
    machine_rating = Float(5000.0, units = 'kW', iotype = 'in', desc = 'rated power for a wind turbine')
    net_aep = Float(1701626526.28, units = 'kW * h', iotype = 'in', desc = 'annual energy production for the plant')

    # parameters
    sea_depth = Float(20.0, units = 'm', iotype = 'in', desc = 'sea depth for offshore wind plant')
    year = Int(2009, units='yr', iotype='in', desc='year for project start')
    month = Int(12, iotype = 'in', desc= 'month for project start') # units = months
    turbine_number = Int(100, iotype = 'in', desc = 'number of turbines at plant')
 
    def __init__(self):
        """
        OpenMDAO component to wrap O&M model of the NREL _cost and Scaling model data (csmOM.py).

        Parameters
        ----------
        machine_rating : float
          rated power for a wind turbine [kW]
        sea_depth : float
          sea depth for offshore wind plant [m]
        year : int
          year for project start
        month : int
          month for project start
        turbine_number : int
          number of turbines at plant
        net_aep : float
          annual energy production for the plant [kWh]
        
        Returns
        -------
        OnMcost : float
          O&M costs [USD]
        plantOM : PlantOM
          Variable tree for detailed O&M outputs    
        """
        super(om_csm_component, self).__init__()

    def execute(self):
        """
        Execute the O&M Model of the NREL _cost and Scaling Model.
        """
        print "In {0}.execute()...".format(self.__class__)

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

        self.OPEX_breakdown.preventative_opex = cost * costEscalator # in $/year

        #LRC        
        if not offshore: 
            lrcCF = 10.70 # land based
            costlrcEscFactor = ppi.compute('IPPI_LLR')
        else: #TODO: transition and deep water options if applicable
            lrcCF = 17.00 # offshore
            ppi.ref_yr = 2003
            costlrcEscFactor = ppi.compute('IPPI_OLR')
            ppi.ref_yr = 2002 
                
        self.OPEX_breakdown.corrective_opex = self.machine_rating * lrcCF * costlrcEscFactor * self.turbine_number # in $/yr

        #LLC
        if not offshore: 
            leaseCF = 0.00108 # land based
            costlandEscFactor = ppi.compute('IPPI_LSE')
        else: #TODO: transition and deep water options if applicable
            leaseCF = 0.00108 # offshore
            costlandEscFactor = ppi.compute('IPPI_LSE')

        self.OPEX_breakdown.lease_opex = self.net_aep * leaseCF * costlandEscFactor # in $/yr

        #Other
        self.OPEX_breakdown.other_opex = 0.0

        #Total OPEX
        self.avg_annual_opex = self.OPEX_breakdown.preventative_opex + self.OPEX_breakdown.corrective_opex \
           + self.OPEX_breakdown.lease_opex
        
        
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

    def linearize(self):
        
        self.J = np.array([[self.d_preventative_d_aep, self.d_preventative_d_rating], [self.d_corrective_d_aep, self.d_corrective_d_rating],\
                           [self.d_lease_d_aep, self.d_lease_d_rating], [self.d_other_d_aep, self.d_other_d_rating],\
                           [self.d_opex_d_aep, self.d_opex_d_rating]])
    
    def provideJ(self):

        inputs = ['net_aep', 'machine_rating']        
        outputs = ['OPEX_breakdown.preventative_opex', 'OPEX_breakdown.corrective_opex', 'OPEX_breakdown.lease_opex', \
                  'OPEX_breakdown.other_opex', 'avg_annual_opex']
        
        return inputs, outputs, self.J


def example():

    # simple test of module

    om = om_csm_assembly()
    
    om.machine_rating = 5000.0 # Need to manipulate input or underlying component will not execute
    om.net_aep = 1701626526.28
    om.sea_depth = 20.0
    om.year = 2010
    om.month = 12
    om.turbine_number = 100

    om.execute()
    print "OM offshore {:.1f}".format(om.avg_annual_opex)
    print "OM by turbine {0}".format(om.OPEX_breakdown.preventative_opex / om.turbine_number)
    print "LRC by turbine {0}".format(om.OPEX_breakdown.corrective_opex / om.turbine_number)
    print "LLC by turbine {0}".format(om.OPEX_breakdown.lease_opex / om.turbine_number)
    print

    om.sea_depth = 0.0
    om.execute()
    print "OM onshore {:.1f}".format(om.avg_annual_opex)
    print "OM by turbine {0}".format(om.OPEX_breakdown.preventative_opex / om.turbine_number)
    print "LRC by turbine {0}".format(om.OPEX_breakdown.corrective_opex / om.turbine_number)
    print "LLC by turbine {0}".format(om.OPEX_breakdown.lease_opex / om.turbine_number)

if __name__ == "__main__":

    example()