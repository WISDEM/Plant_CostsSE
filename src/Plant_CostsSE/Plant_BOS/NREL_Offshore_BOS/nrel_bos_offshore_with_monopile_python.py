"""
bos_nrel_offshore_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Str, Array, VarTree

from fusedwind.plant_cost.fused_costs_asym import BOSVarTree, ExtendedBOSCostAggregator, ExtendedBOSCostModel

from foundation_costSE import foundation_mc_component

class bos_nrel_offshore_assembly(ExtendedBOSCostModel):

    sea_depth = Float(20.0, units = 'm', iotype='in', desc = 'project site water depth')
    
    def __init__(self, ssfile):

        self.ssfile = ssfile
    
        super(bos_nrel_offshore_assembly, self).__init__()

    def configure(self):

        super(bos_nrel_offshore_assembly, self).configure()
    
        self.replace('bos', bos_nrel_offshore_component())
        self.add('foundation', foundation_mc_component())
        
        self.driver.workflow.add('foundation')

        self.connect('sea_depth', ['bos.sea_depth', 'foundation.sea_depth'])
        self.create_passthrough('bos.blade_length')
        self.create_passthrough('bos.blade_width')
        self.create_passthrough('bos.hub_diameter')
        self.create_passthrough('bos.nacelle_length')
        self.create_passthrough('bos.nacelle_height')
        self.create_passthrough('bos.nacelle_width')
        self.create_passthrough('bos.tower_length')
        self.create_passthrough('bos.max_tower_diameter')
        self.create_passthrough('bos.distance_from_shore')
        self.create_passthrough('bos.soil_type')

        self.create_passthrough('foundation.monopileMass')
        self.create_passthrough('foundation.transitionMass')
        self.connect('machine_rating', 'foundation.ratedPower')
        
        self.connect('foundation.foundation_cost', 'bos.foundation_cost')

class bos_nrel_offshore_component(ExtendedBOSCostAggregator):
    """ Evaluates the NREL BOS spreadsheet """

    # variables
    blade_length = Float(units = 'm', iotype='in', desc= 'length of a wind turbine blade')
    blade_width = Float(units = 'm', iotype='in', desc= 'width of blade at max chord position')
    hub_diameter = Float(units = 'm', iotype='in', desc = 'diameter of the hub')
    nacelle_length = Float(units = 'm', iotype='in', desc='length of the nacelle')
    nacelle_height = Float(units = 'm', iotype = 'in', desc = 'height of the nacelle')
    nacelle_width = Float(units = 'm', iotype = 'in', desc = 'width of the nacelle')
    tower_length = Float(units = 'm', iotype = 'in', desc = 'length of tower')
    max_tower_diameter = Float(units = 'm', iotype='in', desc = 'maximum diameter of the tower')
    sea_depth = Float(units = 'm', iotype='in', desc = 'sea depth for offshore wind project')
    foundation_cost = Float(0.0, units='USD', iotype='in', desc='cost for a foundation - 0.0 unless it is a monopile')
    #machine_rating = Float(iotype='in', units='kW', desc='turbine machine rating')
    #rotor_diameter=Float(iotype='in', units='m', desc='rotor diameter')
    #hub_height = Float(iotype='in', units='m', desc='hub height')
    #RNA_mass = Float(iotype='in', units='kg', desc='Rotor Nacelle Assembly mass')
    #turbine_cost = Float(iotype='in', units='USD', desc='Single Turbine Capital _costs')
    #turbine_number = Int(iotype='in', desc='number of turbines in project')    

    # parameters
    distance_from_shore = Float(30.0, units = 'km', iotype='in', desc = 'distance of plant from shore')
    soil_type = Enum('Sand', ('Sand', 'Clay'), iotype='in', desc = 'soil type at plant site')    
    foundation_type = Enum('Monopile', ('Monopile', 'Jacket', 'GBS'), iotype='in', desc='foundation type')
    installation_method = Enum('Preassembled1', ('Preassembled1','Preassembled2', 'FullPre', 'Bunny1', 'Bunny2', 'Individual'), iotype='in', desc='installation method')
    staging_port = Bool(True,iotype='in', desc='boolean for using a staging port')
    plant_voltage = Float(33.0, units='kV', iotype='in', desc='wind farm voltage')
    export_voltage = Float(220.0, units='kV', iotype='in', desc='export voltage')
    array_spacing = Int(8, iotype='in', desc='array spacing rotor diameter multiplier')
    array_layout = Enum('Radial', ('Radial'), iotype='in', desc='array cable layout - not used')
    inspection_clearance = Float(2.0, units='m', iotype='in', desc='inspection clearance')

    # outputs
    #BOS_breakdown = VarTree(BOSVarTree(), iotype='out', desc='BOS cost breakdown')
    
    def __init__(self):
    	  
    	  super(bos_nrel_offshore_component,self).__init__()
        
    def execute(self):
        """
        Executes NREL BOS Offshore Excel model to estimate wind plant BOS costs.
        """
        print "In {0}.execute()...".format(self.__class__)

        # calculated inputs
        area_per_turbine_pre = (self.nacelle_length + self.inspection_clearance) * (self.nacelle_width + self.inspection_clearance) + \
                                  (self.hub_diameter + self.inspection_clearance)**2.0 + \
                                  (self.blade_length + self.inspection_clearance) * (self.blade_width + self.inspection_clearance) + \
                                  (self.tower_length + self.inspection_clearance) * (self.max_tower_diameter + self.inspection_clearance)
                                  (self.rotor_diameter)**2.0
        area_per_turbine_single = (self.nacelle_length + self.hub_diameter + self.inspection_clearance) * (self.nacelle_width + self.inspection_clearance) + \
                                  (self.blade_length + self.inspection_clearance) * (self.blade_width + self.inspection_clearance) + \
                                  (self.tower_length + self.inspection_clearance) * (self.max_tower_diameter + self.inspection_clearance)
                                 
        # Development (engineering and permitting)
        self.BOS_breakdown.development_costs = (1550.0 + 6060.0) * 1000.0
        if (self.foundation_type = 'Monopile'):
        	  self.BOS_breakdown.development_costs += 1500.0 * 1000.0
        else:
        	  self.BOS_breakdown.development_costs += 3000.0 * 1000.0

        # Preparation and Staging Costs (ports)
        self.BOS_breakdown.preparation_and_staging_costs = 
        
        # Foundations and substructure (Only implementing for monopile type at the moment)
        if self.foundation_type = 'Monopile':
            self.BOS_breakdown.foundation_and_substructure_costs = self.foundation_cost
        else:
        	  self.BOS_breakdown.foundation_and_substructure_costs = 0.0
        
        # Electrical costs
        spacing = self.array_spacing * self.rotor_diameter
        power_factor = 0.95
        turbine_current = (self.machine_rating * 1000. * 1000.) / (self.plant_voltage * 1000. * power_factor * (3.**(1./3.)))

        self.BOS_breakdown.electrical_costs = 
        
        # Assembly and Installation (vessels)
        self.BOS_breakdown.assembly_and_installation_costs = 
        
        # Soft costs (decomissioning)
        self.BOS_breakdown.soft_costs = 

        # overall BOS costs
        self.bos_costs = self.BOS_breakdown.development_costs + self.BOS_breakdown.prepration_and_staging_costs + \
                         self.BOS_breakdown.foundation_and_substructure_costs + self.BOS_breakdown.electrical_costs + \
                         self.BOS_breakdown.assembly_and_installation_costs + self.BOS_breakdown.soft_costs
        construction_financing_rate = 0.03
        self.bos_costs      += (self.bos_costs + self.turbine_cost*self.turbine_number)*construction_financing_rate        

        # uncalculated costs
        self.BOS_breakdown.transportation_costs = 0.0
        self.BOS_breakdown.other_costs = 0.0

#----------------------------

def example():  

    bos = bos_nrel_offshore_component()
    bos.machine_rating = 5000.0
    bos.rotor_diameter = 126.0
    bos.turbine_cost = 5950209.283
    bos.turbine_number = 100
    bos.hub_height = 90.0
    bos.RNA_mass = 350000.0
    bos.blade_length = 6.15
    bos.blade_width = 2.3
    bos.hub_diameter = 3.0
    bos.nacelle_length = 17.0
    bos.nacelle_height = 5.5
    bos.nacelle_width = 5.5
    bos.tower_length = 83.0
    bos.max_tower_diameter = 6.0
    bos.sea_depth = 30.0
    bos.foundation_cost = 333212.5

    bos.execute()

    print "Cost {:.3f} found at ({:.2f}) turbines".format(bos.bos_costs, bos.turbine_number) 
    print bos.BOS_breakdown.development_costs
    print bos.BOS_breakdown.preparation_and_staging_costs
    print bos.BOS_breakdown.foundation_and_substructure_costs
    print bos.BOS_breakdown.electrical_costs
    print bos.BOS_breakdown.assembly_and_installation_costs
    print bos.BOS_breakdown.soft_costs

if __name__ == "__main__":
    
    example()