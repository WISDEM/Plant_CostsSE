"""
om_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from fusedwind.plant_cost.fused_costs_asym import OPEXVarTree, ExtendedOPEXAggregator, ExtendedOPEXModel

from NREL_CSM.csmOM import csmOM

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
    sea_depth = Float(20.0, units = 'm', iotype = 'in', desc = 'sea depth for offshore wind plant')
    net_aep = Float(1701626526.28, units = 'kW * h', iotype = 'in', desc = 'annual energy production for the plant')

    # parameters
    year = Int(2009, units='yr', iotype='in', desc='year for project start')
    month = Int(12,  units='mon', iotype = 'in', desc= 'month for project start')
    turbine_number = Int(100, iotype = 'in', desc = 'number of turbines at plant')
 
    def __init__(self):
        """
        OpenMDAO component to wrap O&M model of the NREL Cost and Scaling model data (csmOM.py).

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
        Execute the O&M Model of the NREL Cost and Scaling Model.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.csmOM = csmOM()
        
        self.aepTurbine = self.net_aep / self.turbine_number
        self.csmOM.compute(self.aepTurbine, self.sea_depth, self.machine_rating, self.year, self.month)

        self.OPEX_breakdown.preventative_opex = self.csmOM.getOMCost() * self.turbine_number
        self.OPEX_breakdown.corrective_opex = self.csmOM.getLRC() * self.turbine_number
        self.OPEX_breakdown.lease_opex = self.csmOM.getLLC() * self.turbine_number
        self.OPEX_breakdown.other_opex = 0.0
        self.avg_annual_opex = self.OPEX_breakdown.preventative_opex + self.OPEX_breakdown.corrective_opex \
           + self.OPEX_breakdown.lease_opex


def example():

    # simple test of module

    om = om_csm_assembly()
    
    om.machine_rating = 5000.0 # Need to manipulate input or underlying component will not execute

    om.execute()
    print "OM onshore {:.1f}".format(om.avg_annual_opex)
    print "OM by turbine {0}".format(om.OPEX_breakdown.preventative_opex / om.turbine_number)
    print "LRC by turbine {0}".format(om.OPEX_breakdown.corrective_opex / om.turbine_number)
    print "LLC by turbine {0}".format(om.OPEX_breakdown.lease_opex / om.turbine_number)
    
    om.sea_depth = 0.0
    om.execute()
    print "OM offshore {:.1f}".format(om.avg_annual_opex)
    print "OM by turbine {0}".format(om.OPEX_breakdown.preventative_opex / om.turbine_number)
    print "LRC by turbine {0}".format(om.OPEX_breakdown.corrective_opex / om.turbine_number)
    print "LLC by turbine {0}".format(om.OPEX_breakdown.lease_opex / om.turbine_number)

if __name__ == "__main__":

    example()