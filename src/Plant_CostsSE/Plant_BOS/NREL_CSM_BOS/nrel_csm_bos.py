"""
bos_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from fusedwind.plant_cost.fused_costs_asym import BOSVarTree, ExtendedBOSCostAggregator, ExtendedBOSCostModel

from NREL_CSM.csmBOS import csmBOS
from NREL_CSM.csmFoundation import csmFoundation

class bos_csm_assembly(ExtendedBOSCostModel):

    def configure(self):

        super(bos_csm_assembly, self).configure()
    
        self.replace('bos', bos_csm_component())

        self.create_passthrough('bos.sea_depth')
        self.create_passthrough('bos.year')
        self.create_passthrough('bos.month')

class bos_csm_component(ExtendedBOSCostAggregator):

    # parameters
    sea_depth = Float(20.0, units = 'm', iotype = 'in', desc = 'sea depth for offshore wind plant')
    year = Int(2009, units='yr', iotype='in', desc='year for project start')
    month = Int(12,  units='mon', iotype = 'in', desc= 'month for project start')

    def __init__(self):
        """
        OpenMDAO component to wrap BOS model of the NREL _cost and Scaling Model (csmBOS.py)
        
        Parameters
        ----------
        rotor_diameter : float
          rotor diameter of the machine [m]
        machine_rating : float
          rated power for a wind turbine [kW]
        hub_height : float
          hub height for wind turbine [m]
        sea_depth : float
          sea depth for offshore wind plant [m]
        turbine_cost : float
          Turbine capital costs per turbine [USD]
        year : int
          year of project start
        month : int
          month of project start
        turbine_number : int
          number of turbines at plant
          
        Returns
        -------
        BOS_cost : float
          Balance of station total costs excluding foundation
        plantBOS : PlantBOS
          Variable tree container for detailed BOS cost breakdown based on NREL Offshore _cost Breakdown Structure
        
        """
        super(bos_csm_component, self).__init__()

    def execute(self):
        """
        Executes BOS model of the NREL _cost and Scaling Model to estimate wind plant BOS costs.
        """

        print "In {0}.execute()...".format(self.__class__)

        self.csmBOS = csmBOS()
        self.csmBOS.compute(self.sea_depth,self.machine_rating,self.hub_height,self.rotor_diameter, self.turbine_cost, self.year, self.month)

        self.bos_costs = self.csmBOS.getCost() * self.turbine_number

        [foundation, landTransportation, landCivil, portsStaging, installation, electricalInterconnect, development_cost, \
         accessEquipment, scour, additional] = self.csmBOS.getDetailedCosts()
         
        self.BOS_breakdown.management_costs = 0.0
        self.BOS_breakdown.development_costs = development_cost * self.turbine_number
        self.BOS_breakdown.preparation_and_staging_costs = (landCivil + portsStaging) * self.turbine_number
        self.BOS_breakdown.transportation_costs = (landTransportation * self.turbine_number)
        self.BOS_breakdown.foundation_and_substructure_costs = foundation * self.turbine_number
        self.BOS_breakdown.collection_and_substation_costs = 0.0 # TODO: double check ability to split out from interconnect costs
        self.BOS_breakdown.transmission_and_interconnection_costs = electricalInterconnect * self.turbine_number
        self.BOS_breakdown.assembly_and_installation_costs = installation * self.turbine_number
        self.BOS_breakdown.contingencies_and_insurance_costs = 0.0
        self.BOS_breakdown.decommissioning_costs = 0.0
        self.BOS_breakdown.construction_financing_costs = 0.0
        self.BOS_breakdown.other_costs = (accessEquipment + scour + additional) * self.turbine_number
        self.BOS_breakdown.developer_profits = 0.0

class foundation_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine tower
    """

    # variables
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    hub_height = Float(90.0, units = 'm', iotype='in', desc = 'hub height of machine')
    machine_rating = Float(5000.0, units = 'kW', iotype='in', desc=' rated power of machine')
    sea_depth = Float(0.0, units = 'm', iotype='in', desc = 'project site water depth')
    
    # parameters
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')
  
    # outputs
    foundation_cost = Float(0.0, units='USD', iotype='out', desc='cost for a foundation')

    def __init__(self):
        """
        OpenMDAO component to wrap foundation model of the NREL _cost and Scaling Model (csmFoundation.py)

        Parameters
        ---------- 
		    rotor_diameter : float
		      rotor diameter of the machine [m]
		    hub_height : float
		      hub height of machine [m]
		    machine_rating : float
		      rated power of machine [kW]
		    year : int
		      year of project start
		    month : int
		      month of project start
		    sea_depth : float
		      project site water depth [m]
		      
		    Returns
		    -------
    		foundation_cost : float
    		  cost for a foundation [USD]	    
        """

    def execute(self):
        """
        Executes foundation model of the NREL _cost and Scaling model to determine foundation costs for a land-based or offshore plant.
        """

        print "In {0}.execute()...".format(self.__class__)

        self.foundation = csmFoundation()        
        self.foundation.compute(self.machine_rating, self.hub_height, self.rotor_diameter, self.sea_depth, self.year, self.month)

        self.foundation_cost = self.foundation.getCost()    
#-----------------------------------------------------------------

def example_fdn():

    # simple test of module

    fdn = foundation_csm_component()
        
    # First test
    fdn.machine_rating = 5000.0
    fdn.rotor_diameter = 126.0
    fdn.hub_height = 90.0
    fdn.sea_depth = 0.0
    fdn.year = 2009
    fdn.month = 12
    
    fdn.execute()

    print "Onshore foundation"
    print "Foundation cost: {0}".format(fdn.foundation_cost)
    print
    
    fdn.sea_depth = 20.0
    
    fdn.execute()

    print "Offshore foundation"    
    print "Foundation cost: {0}".format(fdn.foundation_cost)


def example():
	
	  # simple test of module
    bos = bos_csm_assembly()
    bos.machine_rating = 5000.0
    bos.rotor_diameter = 126.0
    bos.turbine_cost = 5950209.283
    bos.turbine_number = 100
    bos.hub_height = 90.0
    bos.RNA_mass = 256634.5 # RNA mass is not used in this simple model
    bos.execute()
    print "BOS cost offshore: {0}".format(bos.bos_costs)
    print "BOS cost per turbine: {0}".format(bos.bos_costs / bos.turbine_number)
    print
    
    bos.sea_depth = 0.0
    bos.turbine_cost = 5229222.77
    bos.execute()
    print "BOS cost onshore: {0}".format(bos.bos_costs)
    print "BOS cost per turbine: {0}".format(bos.bos_costs / bos.turbine_number)
    print

if __name__ == "__main__":

    example()
    
    example_fdn()