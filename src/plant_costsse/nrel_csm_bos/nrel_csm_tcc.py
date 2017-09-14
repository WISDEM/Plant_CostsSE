"""
tcc_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import numpy as np

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree, Enum

from commonse.config import *

from fusedwind.plant_cost.fused_tcc import BaseTurbineCostModel, BaseTCCAggregator, configure_base_tcc
from fusedwind.interface import implement_base

##### Rotor

class blades_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine blade
    """
    
    # Variables
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    
    # Parameters
    year = Int(2009, iotype='in', desc = 'year of project start')
    month = Int(12, iotype='in', desc = 'month of project start')
    advanced_blade = Bool(False, iotype='in', desc = 'boolean for use of advanced blade curve')

    # Outputs
    blade_cost = Float(0.0, units='USD', iotype='out', desc='cost for a single wind turbine blade')
    blade_mass = Float(0.0, units='kg', iotype='out', desc='mass for a single wind turbine blade')

    def __init__(self):
        """
        OpenMDAO component to wrap blade model of the NREL _cost and Scaling Model (csmBlades.py)
        
        """
        super(blades_csm_component, self).__init__()

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
        """
        Executes Blade model of the NREL _cost and Scaling Model to estimate wind turbine blade cost and mass.
        """


        if (self.advanced_blade == True):
            massCoeff = 0.4948
            massExp   = 2.5300
        else:
            massCoeff = 0.1452 
            massExp   = 2.9158
        
        self.blade_mass = (massCoeff*(self.rotor_diameter/2.0)**massExp)

        ppi.curr_yr = curr_yr
        ppi.curr_mon = curr_mon

        ppi_labor  = ppi.compute('IPPI_BLL')

        if (self.advanced_blade == True):
            ref_yr = ppi.ref_yr
            ppi.ref_yr = 2003
            ppi_mat   = ppi.compute('IPPI_BLA')
            ppi.ref_yr = ref_yr
            slopeR3   = 0.4019376
            intR3     = -21051.045983
        else:
            ppi_mat   = ppi.compute('IPPI_BLD')
            slopeR3   = 0.4019376
            intR3     = -955.24267
            
        laborCoeff    = 2.7445
        laborExp      = 2.5025
        
        bladeCostCurrent = ( (slopeR3*(self.rotor_diameter/2.0)**3.0 + (intR3))*ppi_mat + \
                                  (laborCoeff*(self.rotor_diameter/2.0)**laborExp)*ppi_labor    ) / (1.0-0.28)
        self.blade_cost = bladeCostCurrent
    
        # derivatives
        self.d_mass_d_diameter = massExp * (massCoeff*(self.rotor_diameter/2.0)**(massExp-1))* (1/2.)
        self.d_cost_d_diameter = (3.0*(slopeR3*(self.rotor_diameter/2.0)**2.0 )*ppi_mat * (1/2.) + \
                                 (laborExp * laborCoeff*(self.rotor_diameter/2.0)**(laborExp-1))*ppi_labor * (1/2.)) / (1.0-0.28)
 
    def list_deriv_vars(self):

    	  inputs = ['rotor_diameter']
    	  outputs = ['blade_mass', 'blade_cost']
    	  
    	  return inputs, outputs
    
    def provideJ(self):
    	  
    	  self.J = np.array([[self.d_mass_d_diameter],[self.d_cost_d_diameter]])    	
    	  
    	  return self.J
         
#-----------------------------------------------------------------

def example_blade():
  
    # simple test of module

    blades = blades_csm_component()
        
    # First test
    blades.rotor_diameter = 126.0
    blades.advanced_blade = False
    blades.year = 2009
    blades.month = 12
    
    blades.execute()
    
    print "Blade csm component"
    print "Blade mass: {0}".format(blades.blade_mass)
    print "Blade cost: {0}".format(blades.blade_cost)

    blades.advanced_blade = True

    blades.execute()
    
    print "Blade csm component, advanced blade"
    print "Blade mass: {0}".format(blades.blade_mass)
    print "Blade cost: {0}".format(blades.blade_cost)

class hub_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine hub
    """

    # Variables
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    blade_mass = Float(17650.67, units='kg', iotype='in', desc='mass of an individual blade')
    
    # Parameters
    year = Int(2009, iotype='in', desc = 'year of project start')
    month = Int(12, iotype='in', desc = 'month of project start')
    blade_number = Int(3, iotype='in', desc= 'number of rotor blades')

    # Outputs
    hub_system_cost = Float(0.0, units='USD', iotype='out', desc='hub system cost')
    hub_system_mass = Float(0.0, units='kg', iotype='out', desc='hub system mass')
    hub_cost = Float(0.0, units='USD', iotype='out', desc='hub cost')
    hub_mass = Float(0.0, units='kg', iotype='out', desc='hub mass')
    pitch_system_cost = Float(0.0, units='USD', iotype='out', desc='pitch system cost')
    pitch_system_mass = Float(0.0, units='kg', iotype='out', desc='pitch system mass')
    spinner_cost = Float(0.0, units='USD', iotype='out', desc='spinner / nose cone cost')
    spinner_mass = Float(0.0, units='kg', iotype='out', desc='spinner / nose cone mass')

    def __init__(self):
        """
        OpenMDAO component to wrap hub model of the NREL _cost and Scaling Model (csmHub.py)  
        """

        super(hub_csm_component, self).__init__()

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
        """
        Executes hub model of the NREL _cost and Scaling model to compute hub system component masses and costs.
        """


        #*** Pitch bearing and mechanism
        pitchBearingMass = 0.1295 * self.blade_mass*self.blade_number + 491.31  # slope*BldMass3 + int
        bearingHousingPct = 32.80 / 100.0
        massSysOffset = 555.0
        self.pitch_system_mass = pitchBearingMass * (1+bearingHousingPct) + massSysOffset
    
        #*** Hub
        self.hub_mass = 0.95402537 * self.blade_mass + 5680.272238
    
        #*** NoseCone/Spinner
        self.spinner_mass = 18.5*self.rotor_diameter +(-520.5)   # GNS

        self.hub_system_mass = self.hub_mass + self.pitch_system_mass + self.spinner_mass

        ppi.curr_yr = curr_yr
        ppi.curr_mon = curr_mon

        #*** Pitch bearing and mechanism    
        bearingCost = (0.2106*self.rotor_diameter**2.6576)
        bearingCostEscalator = ppi.compute('IPPI_PMB')
        self.pitch_system_cost = bearingCostEscalator * ( bearingCost + bearingCost * 1.28 )
    
        #*** Hub
        hubCost2002 = self.hub_mass * 4.25 # $/kg       
        hubCostEscalator = ppi.compute('IPPI_HUB')
        self.hub_cost = hubCost2002 * hubCostEscalator
    
        #*** NoseCone/Spinner
        spinnerCostEscalator = ppi.compute('IPPI_NAC')
        self.spinner_cost = spinnerCostEscalator * (5.57*self.spinner_mass)         

        self.hub_system_cost = self.hub_cost + self.pitch_system_cost + self.spinner_cost
        
        # derivatives
        self.d_hub_mass_d_diameter = 0.0
        self.d_pitch_mass_d_diameter = 0.0
        self.d_spinner_mass_d_diameter = 18.5
        self.d_system_mass_d_diameter = self.d_hub_mass_d_diameter + self.d_pitch_mass_d_diameter + self.d_spinner_mass_d_diameter
        
        self.d_hub_cost_d_diameter = 0.0
        self.d_pitch_cost_d_diameter = bearingCostEscalator * 2.28 * 2.6576 * (0.2106 * self.rotor_diameter**1.6576)
        self.d_spinner_cost_d_diameter = spinnerCostEscalator * (5.57*self.d_spinner_mass_d_diameter)
        self.d_system_cost_d_diameter = self.d_hub_cost_d_diameter + self.d_pitch_cost_d_diameter + self.d_spinner_cost_d_diameter

        self.d_hub_mass_d_blade_mass = 0.95402537 
        self.d_pitch_mass_d_blade_mass = 0.1295 *self.blade_number * (1+bearingHousingPct)
        self.d_spinner_mass_d_blade_mass = 0.0
        self.d_system_mass_d_blade_mass = self.d_hub_mass_d_blade_mass + self.d_pitch_mass_d_blade_mass + self.d_spinner_mass_d_blade_mass
        
        self.d_hub_cost_d_blade_mass = self.d_hub_mass_d_blade_mass * 4.25 * hubCostEscalator
        self.d_pitch_cost_d_blade_mass = 0.0
        self.d_spinner_cost_d_blade_mass = 0.0
        self.d_system_cost_d_blade_mass = self.d_hub_cost_d_blade_mass + self.d_pitch_cost_d_blade_mass + self.d_spinner_cost_d_blade_mass
        
    def list_deriv_vars(self):

        inputs = ['rotor_diameter', 'blade_mass']
        outputs = ['hub_mass', 'pitch_system_mass', 'spinner_mass', 'hub_system_mass', \
                   'hub_cost', 'pitch_system_cost', 'spinner_cost', 'hub_system_cost']
        
        return inputs, outputs
    
    def provideJ(self):
        
        self.J = np.array([[self.d_hub_mass_d_diameter, self.d_hub_mass_d_blade_mass],\
                           [self.d_pitch_mass_d_diameter, self.d_pitch_mass_d_blade_mass],\
                           [self.d_spinner_mass_d_diameter, self.d_spinner_mass_d_blade_mass],\
                           [self.d_system_mass_d_diameter, self.d_system_mass_d_blade_mass],\
                           [self.d_hub_cost_d_diameter, self.d_hub_cost_d_blade_mass],\
                           [self.d_pitch_cost_d_diameter, self.d_pitch_cost_d_blade_mass],\
                           [self.d_spinner_cost_d_diameter, self.d_spinner_cost_d_blade_mass],\
                           [self.d_system_cost_d_diameter, self.d_system_cost_d_blade_mass]])
        
        return self.J
        
#-----------------------------------------------------------------

def example_hub():

    # simple test of module

    hub = hub_csm_component()
        
    # First test
    hub.blade_mass = 25614.377
    hub.rotor_diameter = 126.0
    hub.blade_number = 3
    hub.year = 2009
    hub.month = 12
    
    hub.execute()
    
    print "Hub csm component"
    print "Hub system mass: {0}".format(hub.hub_system_mass)
    print "Hub mass: {0}".format(hub.hub_mass)
    print "pitch system mass: {0}".format(hub.pitch_system_mass)
    print "spinner mass: {0}".format(hub.spinner_mass)
    print "Hub system cost: {0}".format(hub.hub_system_cost)


##### Nacelle

class nacelle_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine nacelle
    """

    # Variables
    rotor_diameter = Float(126.0, units='m', iotype='in', desc = 'diameter of the rotor')
    rotor_mass = Float(123193.3010, iotype='in', units='kg', desc = 'mass of rotor including blades and hub')
    rotor_thrust = Float(500930.0837, iotype='in', units='N', desc='maximum thurst from rotor')    
    rotor_torque = Float(4365248.7375, iotype='in', units='N * m', desc = 'torque from rotor at rated power')
    machine_rating = Float(5000.0, units='kW', iotype='in', desc = 'Machine rated power')

    # Parameters
    drivetrain_design = Enum('geared', ('geared', 'single_stage', 'multi_drive', 'pm_direct_drive'), iotype='in')
    crane = Bool(True, iotype='in', desc = 'boolean for presence of a service crane up tower')
    advanced_bedplate = Int(0, iotype='in', desc= 'indicator for drivetrain bedplate design 0 - conventional')   
    year = Int(2009, iotype='in', desc = 'year of project start')
    month = Int(12, iotype='in', desc = 'month of project start')
    offshore = Bool(True, iotype='in', desc = 'boolean for land or offshore wind project')

    # Outputs
    nacelle_mass = Float(0.0, units='kg', iotype='out', desc='nacelle mass')
    lowSpeedShaft_mass = Float(0.0, units='kg', iotype='out', desc= 'low speed shaft mass')
    bearings_mass = Float(0.0, units='kg', iotype='out', desc= 'bearings system mass')
    gearbox_mass = Float(0.0, units='kg', iotype='out', desc= 'gearbox and housing mass')
    mechanicalBrakes_mass = Float(0.0, units='kg', iotype='out', desc= 'high speed shaft, coupling, and mechanical brakes mass')
    generator_mass = Float(0.0, units='kg', iotype='out', desc= 'generator and housing mass')
    VSElectronics_mass = Float(0.0, units='kg', iotype='out', desc= 'variable speed electronics mass')
    yawSystem_mass = Float(0.0, units='kg', iotype='out', desc= 'yaw system mass')
    mainframeTotal_mass = Float(0.0, units='kg', iotype='out', desc= 'mainframe total mass including bedplate')
    electronicCabling_mass = Float(0.0, units='kg', iotype='out', desc= 'electronic cabling mass')
    HVAC_mass = Float(0.0, units='kg', iotype='out', desc= 'HVAC system mass')
    nacelleCover_mass = Float(0.0, units='kg', iotype='out', desc= 'nacelle cover mass')
    controls_mass = Float(0.0, units='kg', iotype='out', desc= 'control system mass')

    nacelle_cost = Float(0.0, units='USD', iotype='out', desc='nacelle cost')
    lowSpeedShaft_cost = Float(0.0, units='kg', iotype='out', desc= 'low speed shaft _cost')
    bearings_cost = Float(0.0, units='kg', iotype='out', desc= 'bearings system _cost')
    gearbox_cost = Float(0.0, units='kg', iotype='out', desc= 'gearbox and housing _cost')
    mechanicalBrakes_cost = Float(0.0, units='kg', iotype='out', desc= 'high speed shaft, coupling, and mechanical brakes _cost')
    generator_cost = Float(0.0, units='kg', iotype='out', desc= 'generator and housing _cost')
    VSElectronics_cost = Float(0.0, units='kg', iotype='out', desc= 'variable speed electronics _cost')
    yawSystem_cost = Float(0.0, units='kg', iotype='out', desc= 'yaw system _cost')
    mainframeTotal_cost = Float(0.0, units='kg', iotype='out', desc= 'mainframe total _cost including bedplate')
    electronicCabling_cost = Float(0.0, units='kg', iotype='out', desc= 'electronic cabling _cost')
    HVAC_cost = Float(0.0, units='kg', iotype='out', desc= 'HVAC system _cost')
    nacelleCover_cost = Float(0.0, units='kg', iotype='out', desc= 'nacelle cover _cost')
    controls_cost = Float(0.0, units='kg', iotype='out', desc= 'control system _cost')

    def __init__(self):
        """
        OpenMDAO component to wrap nacelle mass-cost model based on the NREL _cost and Scaling model data (csmNacelle.py).             
        """

        super(nacelle_csm_component, self).__init__()

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
        """
        Execute nacelle model of the NREL _cost and Scaling Model.
        """



        # basic variable initialization        
        if self.offshore == False:
           offshore = 0
        else:
           offshore = 1

        ppi.curr_yr = self.year
        ppi.curr_mon = self.month

        # Low Speed Shaft
        lenShaft  = 0.03 * self.rotor_diameter                                                                   
        mmtArm    = lenShaft / 5                                                                 
        bendLoad  = 1.25*9.81*self.rotor_mass                                                           
        bendMom   = bendLoad * mmtArm                                                                 
        hFact     = 0.1                                                                                    
        hollow    = 1/(1-(hFact)**4)                                                                   
        outDiam   = ((32./np.pi)*hollow*3.25*((self.rotor_torque*3./371000000.)**2+(bendMom/71070000)**2)**(0.5))**(1./3.) 
        inDiam    = outDiam * hFact 
                                                                              
        self.lowSpeedShaft_mass      = 1.25*(np.pi/4)*(outDiam**2-inDiam**2)*lenShaft*7860

        LowSpeedShaftCost2002 = 0.0998 * self.rotor_diameter ** 2.8873
        lssCostEsc     = ppi.compute('IPPI_LSS')
        
        self.lowSpeedShaft_cost = LowSpeedShaftCost2002 * lssCostEsc

        d_mass_d_outD = 1.25*(np.pi/4) * (1 - 0.1**2) * 2 * outDiam * lenShaft*7860
        d_outD_mult = ((32./np.pi)*hollow*3.25)**(1./3.) * (1./6.) * ((self.rotor_torque*3./371000000.)**2+(bendMom/71070000.)**2)**(-5./6.)
        d_outD_d_diameter = d_outD_mult * 2. * (bendMom/71070000) * (1./71070000.) * (bendLoad * 0.03 / 5)
        d_outD_d_mass = d_outD_mult * 2. * (bendMom/71070000) * (1./71070000.) * (mmtArm * 1.25 * 9.81)
        d_outD_d_torque = d_outD_mult * 2. * (self.rotor_torque*3./371000000.) * (3./371000000.)
        self.d_lss_mass_d_r_diameter = d_mass_d_outD * d_outD_d_diameter + \
                                       1.25*(np.pi/4)*(outDiam**2-inDiam**2)*7860 * 0.03
        self.d_lss_mass_d_r_mass = d_mass_d_outD * d_outD_d_mass
        self.d_lss_mass_d_r_torque = d_mass_d_outD * d_outD_d_torque

        self.d_lss_cost_d_r_diameter = lssCostEsc * 2.8873 * 0.0998 * self.rotor_diameter ** 1.8873
        
        # Gearbox
        costCoeff = [None, 16.45  , 74.101     ,   15.25697015,  0 ]
        costExp   = [None,  1.2491,  1.002     ,    1.2491    ,  0 ]
        massCoeff = [None, 65.601 , 81.63967335,  129.1702924 ,  0 ]
        massExp   = [None,  0.759 ,  0.7738    ,    0.7738    ,  0 ]
        
        if self.drivetrain_design == 'geared':
            drivetrain_design = 1
        elif self.drivetrain_design == 'single_stage':
            drivetrain_design = 2
        elif self.drivetrain_design == 'multi-drive':
            drivetrain_design = 3
        elif self.drivetrain_design == 'pm_direct_drive':
            drivetrain_design = 4

        self.gearbox_mass = massCoeff[drivetrain_design] * (self.rotor_torque/1000) ** massExp[drivetrain_design] 

        gearboxCostEsc     = ppi.compute('IPPI_GRB')        
        Gearbox2002 = costCoeff[drivetrain_design] * self.machine_rating ** costExp[drivetrain_design]  
        self.gearbox_cost = Gearbox2002 * gearboxCostEsc   
        
        if drivetrain_design == 4:
            self.d_gearbox_mass_d_r_torque = 0.0
            self.d_gearbox_cost_d_rating = 0.0
        else:
            self.d_gearbox_mass_d_r_torque = massExp[drivetrain_design]  * massCoeff[drivetrain_design] * ((self.rotor_torque/1000.) ** (massExp[drivetrain_design] - 1)) * (1/1000.)
            self.d_gearbox_cost_d_rating = gearboxCostEsc * costExp[drivetrain_design] * costCoeff[drivetrain_design] * self.machine_rating ** (costExp[drivetrain_design] - 1)

        # Generator
        costCoeff = [None, 65.000, 54.72533,  48.02963 , 219.3333 ] # $/kW - from 'Generators' worksheet
        massCoeff = [None, 6.4737, 10.50972,  5.343902 , 37.68400 ]
        massExp   = [None, 0.9223, 0.922300,  0.922300 , 1.000000 ]

        if (drivetrain_design < 4):
            self.generator_mass = massCoeff[drivetrain_design] * self.machine_rating ** massExp[drivetrain_design]   
        else:  # direct drive
            self.generator_mass = massCoeff[drivetrain_design] * self.rotor_torque ** massExp[drivetrain_design] 

        generatorCostEsc     = ppi.compute('IPPI_GEN')                                                  
        GeneratorCost2002 = costCoeff[drivetrain_design] * self.machine_rating 
        self.generator_cost = GeneratorCost2002 * generatorCostEsc

        if drivetrain_design < 4:
            self.d_generator_mass_d_r_torque = 0.0
            self.d_generator_mass_d_rating = massExp[drivetrain_design] * massCoeff[drivetrain_design] * self.machine_rating ** (massExp[drivetrain_design]-1)
        else:
            self.d_generator_mass_d_r_torque = massExp[drivetrain_design] * massCoeff[drivetrain_design] * self.rotor_torque ** (massExp[drivetrain_design]-1)
            self.d_generator_mass_d_rating = 0.0
        self.d_generator_cost_d_rating = generatorCostEsc * costCoeff[drivetrain_design]
        
        # Rest of the system
        
        # --- electrical connections           
        self.electronicCabling_mass = 0.0
        
        # --- bearings           
        self.bearings_mass = 0.00012266667 * (self.rotor_diameter ** 3.5) - 0.00030360 * (self.rotor_diameter ** 2.5)
        HousingMass  = self.bearings_mass 
        self.bearings_mass  += HousingMass
        
        self.d_bearings_mass_d_r_diameter = 2 * ( 3.5 * 0.00012266667 * (self.rotor_diameter ** 2.5) - 0.00030360 * 2.5 * (self.rotor_diameter ** 1.5))
        
        # --- mechanical brake           
        mechBrakeCost2002 = 1.9894 * self.machine_rating + (-0.1141)
        self.mechanicalBrakes_mass = mechBrakeCost2002 * 0.10
        
        self.d_brakes_mass_d_rating = 0.10 * 1.9894
        
        # --- variable-speed electronics
        self.VSElectronics_mass = 0.0

        # --- yaw drive bearings
        self.yawSystem_mass = 1.6 * (0.0009 * self.rotor_diameter ** 3.314)
        
        self.d_yaw_mass_d_r_diameter = 3.314 * 1.6 * (0.0009 * self.rotor_diameter ** 2.314)
        
        # --- hydraulics, cooling
        self.HVAC_mass = 0.08 * self.machine_rating
        
        self.d_hvac_mass_d_rating = 0.08

        # --- bedplate ---        
        if (self.advanced_bedplate == 0):   # not an actual option in cost and scaling model                                           
            BedplateWeightFac = 2.86  # modular
        elif (self.advanced_bedplate == 1): # test for mod-adv
            BedplateWeightFac = 2.40  # modular-advanced
        else:
            BedplateWeightFac = 0.71  # advanced

        # These RD functions from spreadsheet don't quite form a continuous composite function        
        '''if (self.rotor_diameter <= 15.0): # Removing for gradients - assuming large turbines only
            TowerTopDiam = 0.3
        elif (self.rotor_diameter <= 60.0):
            TowerTopDiam = (0.07042*self.rotor_diameter-0.715)
        else:'''
        TowerTopDiam = (12.29*self.rotor_diameter+2648)/1000

        MassFromTorque = BedplateWeightFac * 0.00368 * self.rotor_torque
        MassFromThrust      = 0.00158 * BedplateWeightFac * self.rotor_thrust * TowerTopDiam
        MassFromRotorWeight = 0.015   * BedplateWeightFac * self.rotor_mass     * TowerTopDiam
        
        # Bedplate(Length|Area) added by GNS
        BedplateLength = 1.5874 * 0.052 * self.rotor_diameter
        BedplateArea = 0.5 * BedplateLength * BedplateLength
        MassFromArea = 100 * BedplateWeightFac * BedplateArea

        # mfmCoeff[1,4] for different drivetrain configurations
        mfmCoeff = [None,22448,1.29490,1.72080,22448 ]
        mfmExp   = [None,    0,1.9525, 1.9525 ,    0 ]

        # --- nacelle totals        
        TotalMass = MassFromTorque + MassFromThrust + MassFromRotorWeight + MassFromArea
        
        if (drivetrain_design == 1) or (drivetrain_design == 4):
            self.bedplate_mass = TotalMass
        else:
            self.bedplate_mass = mfmCoeff[drivetrain_design] * (self.rotor_diameter ** mfmExp[drivetrain_design] )

        NacellePlatformsMass = .125 * self.bedplate_mass            
     
        # --- crane ---        
        if (self.crane):
            self.crane_mass =  3000.
        else:
            self.crane_mass = 0.  
            
        # --- main frame ---       
        self.mainframeTotal_mass = self.bedplate_mass + NacellePlatformsMass + self.crane_mass

        if (drivetrain_design == 1) or (drivetrain_design == 4):
            self.d_mainframe_mass_d_r_diameter = 1.125 * (((0.00158 * BedplateWeightFac * self.rotor_thrust * (12.29/1000.)) + \
                                                  (0.015   * BedplateWeightFac * self.rotor_mass * (12.29/1000.)) + \
                                                  (100 * BedplateWeightFac * 0.5 * (1.5874 * 0.052)**2. * (2 * self.rotor_diameter))))
            self.d_mainframe_mass_d_r_mass = 1.125 * (0.015   * BedplateWeightFac * TowerTopDiam)
            self.d_mainframe_mass_d_r_thrust = 1.125 * (0.00158 * BedplateWeightFac * TowerTopDiam)
            self.d_mainframe_mass_d_r_torque = 1.125 * BedplateWeightFac * 0.00368
        else:
            self.d_mainframe_mass_d_r_diameter = 1.125 * mfmCoeff[drivetrain_design] * \
                                                  (mfmExp[drivetrain_design] * self.rotor_diameter ** (mfmExp[drivetrain_design]-1))
            self.d_mainframe_mass_d_r_mass = 0.0
            self.d_mainframe_mass_d_r_thrust = 0.0
            self.d_mainframe_mass_d_r_torque = 0.0      

        # --- nacelle cover ---        
        nacelleCovCost2002 = 11.537 * self.machine_rating + (3849.7)
        self.nacelleCover_mass = nacelleCovCost2002 * 0.111111
        
        self.d_cover_mass_d_rating = 0.111111 * 11.537

        # --- control system ---
        self.controls_mass = 0.0

        # overall mass   
        self.nacelle_mass = self.lowSpeedShaft_mass + \
                    self.bearings_mass + \
                    self.gearbox_mass + \
                    self.mechanicalBrakes_mass + \
                    self.generator_mass + \
                    self.VSElectronics_mass + \
                    self.yawSystem_mass + \
                    self.mainframeTotal_mass + \
                    self.electronicCabling_mass + \
                    self.HVAC_mass + \
                    self.nacelleCover_mass + \
                    self.controls_mass
        
        self.d_nacelle_mass_d_r_diameter = self.d_lss_mass_d_r_diameter + self.d_bearings_mass_d_r_diameter + self.d_yaw_mass_d_r_diameter + self.d_mainframe_mass_d_r_diameter
        self.d_nacelle_mass_d_r_mass = self.d_lss_mass_d_r_mass + self.d_mainframe_mass_d_r_mass
        self.d_nacelle_mass_d_r_thrust = self.d_mainframe_mass_d_r_thrust
        self.d_nacelle_mass_d_r_torque = self.d_lss_mass_d_r_torque + self.d_gearbox_mass_d_r_torque + self.d_generator_mass_d_r_torque + self.d_mainframe_mass_d_r_torque
        self.d_nacelle_mass_d_rating = self.d_generator_mass_d_rating + self.d_brakes_mass_d_rating + self.d_hvac_mass_d_rating + self.d_cover_mass_d_rating
        
        # Rest of System Costs
        # Cost Escalators - obtained from ppi tables
        bearingCostEsc       = ppi.compute('IPPI_BRN')
        mechBrakeCostEsc     = ppi.compute('IPPI_BRK')
        VspdEtronicsCostEsc  = ppi.compute('IPPI_VSE')
        yawDrvBearingCostEsc = ppi.compute('IPPI_YAW')
        nacelleCovCostEsc    = ppi.compute('IPPI_NAC')
        hydrCoolingCostEsc   = ppi.compute('IPPI_HYD')
        mainFrameCostEsc     = ppi.compute('IPPI_MFM')
        econnectionsCostEsc  = ppi.compute('IPPI_ELC')

        # These RD functions from spreadsheet don't quite form a continuous composite function
        
        # --- electrical connections
        self.electronicCabling_cost = 40.0 * self.machine_rating # 2002
        self.electronicCabling_cost *= econnectionsCostEsc
        
        self.d_electronics_cost_d_rating = 40.0 * econnectionsCostEsc
        
        # --- bearings
        bearingMass = 0.00012266667 * (self.rotor_diameter ** 3.5) - 0.00030360 * (self.rotor_diameter ** 2.5)
        HousingMass  = bearingMass 
        brngSysCostFactor = 17.6 # $/kg
        Bearings2002 = bearingMass * brngSysCostFactor
        Housing2002  = HousingMass      * brngSysCostFactor
        self.bearings_cost = ( Bearings2002 + Housing2002 ) * bearingCostEsc
        
        self.d_bearings_cost_d_r_diameter = bearingCostEsc * brngSysCostFactor * self.d_bearings_mass_d_r_diameter
        
        # --- mechanical brake           
        mechBrakeCost2002 = 1.9894 * self.machine_rating + (-0.1141)
        self.mechanicalBrakes_cost = mechBrakeCostEsc * mechBrakeCost2002
        
        self.d_brakes_cost_d_rating = mechBrakeCostEsc * 1.9894
        
        # --- variable-speed electronics           
        VspdEtronics2002 = 79.32 * self.machine_rating
        self.VSElectronics_cost = VspdEtronics2002 * VspdEtronicsCostEsc
        
        self.d_vselectronics_cost_d_rating = VspdEtronicsCostEsc * 79.32

        # --- yaw drive bearings
        YawDrvBearing2002 = 2 * ( 0.0339 * self.rotor_diameter ** 2.9637 )
        self.yawSystem_cost = YawDrvBearing2002 * yawDrvBearingCostEsc
        
        self.d_yaw_cost_d_r_diameter = yawDrvBearingCostEsc * 2 * 2.9637 * ( 0.0339 * self.rotor_diameter ** 1.9637 )
        
        # --- hydraulics, cooling
        self.HVAC_cost = 12.0 * self.machine_rating # 2002
        self.HVAC_cost *= hydrCoolingCostEsc 
        
        self.d_hvac_cost_d_rating = hydrCoolingCostEsc * 12.0
 
        # --- control system ---   
        initControlCost = [ 35000, 55900 ]  # land, off-shore
        self.controls_cost = initControlCost[offshore] * ppi.compute('IPPI_CTL')

        # --- nacelle totals
        NacellePlatforms2002 = 8.7 * NacellePlatformsMass
        
        # --- nacelle cover ---        
        nacelleCovCost2002 = 11.537 * self.machine_rating + (3849.7)
        self.nacelleCover_cost = nacelleCovCostEsc * nacelleCovCost2002
        
        self.d_cover_cost_d_rating = nacelleCovCostEsc * 11.537
        
        # --- crane ---
        
        if (self.crane):
            self.crane_cost = 12000.
        else:
            self.crane_cost = 0.0
            
        # --- main frame ---
        # mfmCoeff[1,4] for different drivetrain configurations
        mfmCoeff = [None,9.4885,303.96,17.923,627.28 ]
        mfmExp   = [None,1.9525,1.0669,1.6716,0.8500 ]
        
        MainFrameCost2002 = mfmCoeff[drivetrain_design] * self.rotor_diameter ** mfmExp[drivetrain_design]
        BaseHardware2002  = MainFrameCost2002 * 0.7
        MainFrame2002 = ( MainFrameCost2002    + 
                          NacellePlatforms2002 + 
                          self.crane_cost       + # service crane 
                          BaseHardware2002 )
        self.mainframeTotal_cost = MainFrame2002 * mainFrameCostEsc
        
        self.d_mainframe_cost_d_r_diameter = mainFrameCostEsc * (1.7 * mfmCoeff[drivetrain_design] * mfmExp[drivetrain_design] * self.rotor_diameter ** (mfmExp[drivetrain_design]-1) + \
                                                                8.7 * self.d_mainframe_mass_d_r_diameter * (0.125/1.125))
        self.d_mainframe_cost_d_r_mass = mainFrameCostEsc * 8.7 * self.d_mainframe_mass_d_r_mass * (0.125/1.125)
        self.d_mainframe_cost_d_r_thrust = mainFrameCostEsc * 8.7 * self.d_mainframe_mass_d_r_thrust * (0.125/1.125)
        self.d_mainframe_cost_d_r_torque = mainFrameCostEsc * 8.7 * self.d_mainframe_mass_d_r_torque * (0.125/1.125)

        # overall system cost  
        self.nacelle_cost = self.lowSpeedShaft_cost + \
                    self.bearings_cost + \
                    self.gearbox_cost + \
                    self.mechanicalBrakes_cost + \
                    self.generator_cost + \
                    self.VSElectronics_cost + \
                    self.yawSystem_cost + \
                    self.mainframeTotal_cost + \
                    self.electronicCabling_cost + \
                    self.HVAC_cost + \
                    self.nacelleCover_cost + \
                    self.controls_cost

        self.d_nacelle_cost_d_r_diameter = self.d_lss_cost_d_r_diameter + self.d_bearings_cost_d_r_diameter + self.d_yaw_cost_d_r_diameter + self.d_mainframe_cost_d_r_diameter
        self.d_nacelle_cost_d_r_mass = self.d_mainframe_cost_d_r_mass
        self.d_nacelle_cost_d_r_thrust = self.d_mainframe_cost_d_r_thrust
        self.d_nacelle_cost_d_r_torque = self.d_mainframe_cost_d_r_torque
        self.d_nacelle_cost_d_rating = self.d_gearbox_cost_d_rating + self.d_generator_cost_d_rating + self.d_brakes_cost_d_rating + self.d_hvac_cost_d_rating + \
                                       self.d_cover_cost_d_rating + self.d_electronics_cost_d_rating + self.d_vselectronics_cost_d_rating

    def list_deriv_vars(self):

        inputs = ['rotor_diameter', 'rotor_mass', 'rotor_thrust', 'rotor_torque', 'machine_rating']
        outputs = ['nacelle_mass', 'lowSpeedShaft_mass', 'bearings_mass', 'gearbox_mass', 'generator_mass', 'mechanicalBrakes_mass', 'yawSystem_mass', \
                   'electronicCabling_mass', 'HVAC_mass', 'VSElectronics_mass', 'mainframeTotal_mass', 'nacelleCover_mass', 'controls_mass',\
                   'nacelle_cost', 'lowSpeedShaft_cost', 'bearings_cost', 'gearbox_cost', 'generator_cost', 'mechanicalBrakes_cost', 'yawSystem_cost', \
                   'electronicCabling_cost', 'HVAC_cost', 'VSElectronics_cost', 'mainframeTotal_cost', 'nacelleCover_cost', 'controls_cost']

        return inputs, outputs
    
    def provideJ(self):
      
        self.J = np.array([[self.d_nacelle_mass_d_r_diameter, self.d_nacelle_mass_d_r_mass, self.d_nacelle_mass_d_r_thrust, self.d_nacelle_mass_d_r_torque, self.d_nacelle_mass_d_rating],\
                           [self.d_lss_mass_d_r_diameter, self.d_lss_mass_d_r_mass, 0.0, self.d_lss_mass_d_r_torque, 0.0],\
                           [self.d_bearings_mass_d_r_diameter, 0.0, 0.0, 0.0, 0.0],\
                           [0.0, 0.0, 0.0, self.d_gearbox_mass_d_r_torque, 0.0],\
                           [0.0, 0.0, 0.0, self.d_generator_mass_d_r_torque, self.d_generator_mass_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, self.d_brakes_mass_d_rating],\
                           [self.d_yaw_mass_d_r_diameter, 0.0, 0.0, 0.0, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, self.d_hvac_mass_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, 0.0],\
                           [self.d_mainframe_mass_d_r_diameter, self.d_mainframe_mass_d_r_mass, self.d_mainframe_mass_d_r_thrust, self.d_mainframe_mass_d_r_torque, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, self.d_cover_mass_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, 0.0],\
                           [self.d_nacelle_cost_d_r_diameter, self.d_nacelle_cost_d_r_mass, self.d_nacelle_cost_d_r_thrust, self.d_nacelle_cost_d_r_torque, self.d_nacelle_cost_d_rating],\
                           [self.d_lss_cost_d_r_diameter, 0.0, 0.0, 0.0, 0.0],\
                           [self.d_bearings_cost_d_r_diameter, 0.0, 0.0, 0.0, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, self.d_gearbox_cost_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, self.d_generator_cost_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, self.d_brakes_cost_d_rating],\
                           [self.d_yaw_cost_d_r_diameter, 0.0, 0.0, 0.0, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, self.d_electronics_cost_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, self.d_hvac_cost_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, self.d_vselectronics_cost_d_rating],\
                           [self.d_mainframe_cost_d_r_diameter, self.d_mainframe_cost_d_r_mass, self.d_mainframe_cost_d_r_thrust, self.d_mainframe_cost_d_r_torque, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, self.d_cover_cost_d_rating],\
                           [0.0, 0.0, 0.0, 0.0, 0.0]])
    
        return self.J
       
#-----------------------------------------------------------------

def example_nacelle():

    # simple test of module

    nac = nacelle_csm_component()
        
    # First test
    nac.rotor_diameter = 126.0
    nac.machine_rating = 5000.0
    nac.rotor_mass = 123193.30
    #nac.max_rotor_speed = 12.12609
    nac.rotor_thrust = 500930.1
    nac.rotor_torque = 4365249
    nac.drivetrain_design = 'geared'
    nac.offshore = True
    nac.crane=True
    nac.advanced_bedplate=0
    nac.year = 2009
    nac.month = 12
    
    nac.execute()
    
    print "Nacelle csm component"
    print "Nacelle mass: {0}".format(nac.nacelle_mass)
    print   
    print "lss mass: {0}".format(nac.lowSpeedShaft_mass)
    print "bearings mass: {0}".format(nac.bearings_mass)
    print "gearbox mass: {0}".format(nac.gearbox_mass)
    print "mechanical brake mass: {0}".format(nac.mechanicalBrakes_mass)
    print "generator mass: {0}".format(nac.generator_mass)
    print "yaw system mass: {0}".format(nac.yawSystem_mass)
    print "mainframe total mass: {0}".format(nac.mainframeTotal_mass)
    print "econnections total mass: {0}".format(nac.electronicCabling_mass)
    print "hvac mass: {0}".format(nac.HVAC_mass)
    print "nacelle cover mass: {0}".format(nac.nacelleCover_mass)
    print "controls mass: {0}".format(nac.controls_mass)
    print
    print "Nacelle cost: {0}".format(nac.nacelle_cost)
    print   
    print "lss _cost: {0}".format(nac.lowSpeedShaft_cost)
    print "bearings _cost: {0}".format(nac.bearings_cost)
    print "gearbox _cost: {0}".format(nac.gearbox_cost)
    print "mechanical brake _cost: {0}".format(nac.mechanicalBrakes_cost)
    print "generator _cost: {0}".format(nac.generator_cost)
    print "yaw system _cost: {0}".format(nac.yawSystem_cost)
    print "mainframe total _cost: {0}".format(nac.mainframeTotal_cost)
    print "econnections total cost: {0}".format(nac.electronicCabling_cost)
    print "hvac cost: {0}".format(nac.HVAC_cost)
    print "nacelle cover cost: {0}".format(nac.nacelleCover_cost)
    print "controls cost: {0}".format(nac.controls_cost)


##### Tower

class tower_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine tower
    """
    
    # Variables
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    hub_height = Float(90.0, units = 'm', iotype='in', desc = 'hub height of machine')
    
    # Parameters
    year = Int(2009, iotype='in', desc = 'year of project start')
    month = Int(12, iotype='in', desc = 'month of project start')
    advanced_tower = Bool(False, iotype='in', desc = 'advanced tower configuration')

    # Outputs 
    tower_cost = Float(0.0, units='USD', iotype='out', desc='cost for a tower')
    tower_mass = Float(0.0, units='kg', iotype='out', desc='mass for a turbine tower')

    def __init__(self):
        """
        OpenMDAO component to wrap tower model based of the NREL _cost and Scaling Model data (csmTower.py).     
        """        

        super(tower_csm_component, self).__init__()

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
        """
        Executes the tower model of the NREL _cost and Scaling Model.
        """

        windpactMassSlope = 0.397251147546925
        windpactMassInt   = -1414.381881
        
        if self.advanced_tower:
           windpactMassSlope = 0.269380169
           windpactMassInt = 1779.328183

        self.tower_mass = windpactMassSlope * np.pi * (self.rotor_diameter/2.)**2 * self.hub_height + windpactMassInt

        ppi.curr_yr = curr_yr
        ppi.curr_mon = curr_mon

        twrCostEscalator  = 1.5944
        twrCostEscalator  = ppi.compute('IPPI_TWR')
        twrCostCoeff      = 1.5 # $/kg    

        self.towerCost2002 = self.tower_mass * twrCostCoeff               
        self.tower_cost = self.towerCost2002 * twrCostEscalator
        
        # derivatives
        self.d_mass_d_diameter = 2 * windpactMassSlope * np.pi * (self.rotor_diameter/2.) * (1/2.) * self.hub_height
        self.d_mass_d_hheight = windpactMassSlope * np.pi * (self.rotor_diameter/2.)**2
        self.d_cost_d_diameter = twrCostCoeff * twrCostEscalator * self.d_mass_d_diameter
        self.d_cost_d_hheight = twrCostCoeff * twrCostEscalator * self.d_mass_d_hheight
    
    def list_deriv_vars(self):

        inputs = ['rotor_diameter', 'hub_height']
        outputs = ['tower_mass', 'tower_cost']
        
        return inputs, outputs
    
    def provideJ(self):

        self.J = np.array([[self.d_mass_d_diameter, self.d_mass_d_hheight], [self.d_cost_d_diameter, self.d_cost_d_hheight]])
        
        return self.J        
          
#-----------------------------------------------------------------

def example_tower():

    # simple test of module

    tower = tower_csm_component()
        
    # First test
    tower.rotor_diameter = 126.0
    tower.hub_height = 90.0
    tower.year = 2009
    tower.month = 12
    
    tower.execute()
    
    print "Tower csm component"
    print "Tower mass: {0}".format(tower.tower_mass)
    print "Tower cost: {0}".format(tower.tower_cost)


##### Turbine

# -------------------------------------------------------
# Rotor mass adder
class rotor_mass_adder(Component):

    # Variables
    blade_mass = Float(0.0, units='kg', iotype='in', desc='mass for a single wind turbine blade')
    hub_system_mass = Float(0.0, units='kg', iotype='in', desc='hub system mass')  
    
    # Parameters
    blade_number = Int(3, iotype='in', desc='blade numebr')
    
    # Outputs
    rotor_mass = Float(units='kg', iotype='out', desc= 'overall rotor mass')

    def __init__(self):
      
        super(rotor_mass_adder,self).__init__()

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
       
        self.rotor_mass = self.blade_mass * self.blade_number + self.hub_system_mass
         
        self.d_mass_d_blade_mass = self.blade_number
        self.d_mass_d_hub_mass = 1.0
         
    def list_deriv_vars(self):

        inputs = ['blade_mass', 'hub_system_mass']
        outputs = ['rotor_mass']
        
        return inputs, outputs
    
    def provideJ(self):
      
        self.J = np.array([[self.d_mass_d_blade_mass, self.d_mass_d_hub_mass]])        
        
        return self.J

# --------------------------------------------------------------------
@implement_base(BaseTurbineCostModel)
class tcc_csm_assembly(Assembly):

    # Variables
    rotor_diameter = Float(units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    machine_rating = Float(units = 'kW', iotype='in', desc = 'rated power of wind turbine')
    hub_height = Float(units = 'm', iotype='in', desc= 'hub height of wind turbine above ground / sea level')
    rotor_thrust = Float(iotype='in', units='N', desc='maximum thurst from rotor')    
    rotor_torque = Float(iotype='in', units='N * m', desc = 'torque from rotor at rated power')

    # Parameters
    year = Int(2009, iotype='in', desc = 'year of project start')
    month = Int(12, iotype='in', desc = 'month of project start')
    blade_number = Int(3, iotype='in', desc = 'number of rotor blades')
    offshore = Bool(True, iotype='in', desc = 'boolean for offshore')
    advanced_blade = Bool(False, iotype='in', desc = 'boolean for use of advanced blade curve')
    drivetrain_design = Enum('geared', ('geared', 'single_stage', 'multi_drive', 'pm_direct_drive'), iotype='in')
    crane = Bool(True, iotype='in', desc = 'boolean for presence of a service crane up tower')
    advanced_bedplate = Int(0, iotype='in', desc= 'indicator for drivetrain bedplate design 0 - conventional')   
    advanced_tower = Bool(False, iotype='in', desc = 'advanced tower configuration')

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')
    rotor_cost = Float(0.0, iotype='out', desc='Rotor cost')
    nacelle_cost = Float(0.0, iotype='out', desc='Nacelle cost')
    tower_cost = Float(0.0, iotype='out', desc='Tower cost')

    def configure(self):

        configure_base_tcc(self)

        self.replace('tcc', tcc_csm_component())
        self.add('blades', blades_csm_component())
        self.add('hub', hub_csm_component())
        self.add('nacelle', nacelle_csm_component())
        self.add('tower', tower_csm_component())
        self.add('rotor', rotor_mass_adder())
        
        self.connect('rotor_diameter', ['blades.rotor_diameter', 'hub.rotor_diameter', 'nacelle.rotor_diameter', 'tower.rotor_diameter'])
        self.connect('machine_rating', 'nacelle.machine_rating')
        self.connect('hub_height', ['tower.hub_height'])
        self.connect('blade_number', ['rotor.blade_number', 'hub.blade_number', 'tcc.blade_number'])
        self.connect('offshore', ['nacelle.offshore', 'tcc.offshore'])
        self.connect('year', ['blades.year', 'hub.year', 'nacelle.year', 'tower.year'])
        self.connect('month', ['blades.month', 'hub.month', 'nacelle.month', 'tower.month'])
        
        self.connect('blades.blade_mass', ['hub.blade_mass', 'rotor.blade_mass'])
        self.connect('hub.hub_system_mass', 'rotor.hub_system_mass')
        self.connect('rotor.rotor_mass', 'nacelle.rotor_mass')
        
        self.connect('advanced_blade','blades.advanced_blade')
        self.connect('rotor_thrust','nacelle.rotor_thrust')
        self.connect('rotor_torque','nacelle.rotor_torque')
        self.connect('crane','nacelle.crane')
        self.connect('advanced_bedplate','nacelle.advanced_bedplate')
        self.connect('drivetrain_design','nacelle.drivetrain_design')
        self.connect('advanced_tower','tower.advanced_tower')
        
        # connect mass and cost outputs to tcc
        self.connect('blades.blade_mass', ['tcc.blade_mass'])
        self.connect('blades.blade_cost', 'tcc.blade_cost')

        self.connect('hub.hub_system_cost', 'tcc.hub_system_cost')
        self.connect('hub.hub_system_mass', 'tcc.hub_system_mass')
        '''self.connect('hub.hub_cost', 'tcc.hub_cost')
        self.connect('hub.hub_mass', 'tcc.hub_mass')
        self.connect('hub.pitch_system_cost', 'tcc.pitch_system_cost')
        self.connect('hub.pitch_system_mass', 'tcc.pitch_system_mass')
        self.connect('hub.spinner_cost', 'tcc.spinner_cost')
        self.connect('hub.spinner_mass', 'tcc.spinner_mass')'''

        self.connect('nacelle.nacelle_mass', 'tcc.nacelle_mass')
        '''self.connect('nacelle.lowSpeedShaft_mass', 'tcc.lowSpeedShaft_mass')
        self.connect('nacelle.bearings_mass', 'tcc.bearings_mass')
        self.connect('nacelle.gearbox_mass', 'tcc.gearbox_mass')
        self.connect('nacelle.mechanicalBrakes_mass', 'tcc.mechanicalBrakes_mass')
        self.connect('nacelle.generator_mass', 'tcc.generator_mass')
        self.connect('nacelle.VSElectronics_mass', 'tcc.VSElectronics_mass')
        self.connect('nacelle.yawSystem_mass', 'tcc.yawSystem_mass')
        self.connect('nacelle.mainframeTotal_mass', 'tcc.mainframeTotal_mass')
        self.connect('nacelle.electronicCabling_mass', 'tcc.electronicCabling_mass')
        self.connect('nacelle.HVAC_mass', 'tcc.HVAC_mass')
        self.connect('nacelle.nacelleCover_mass', 'tcc.nacelleCover_mass')
        self.connect('nacelle.controls_mass', 'tcc.controls_mass')'''

        self.connect('nacelle.nacelle_cost', ['tcc.nacelle_cost', 'nacelle_cost'])
        '''self.connect('nacelle.lowSpeedShaft_cost', 'tcc.lowSpeedShaft_cost')
        self.connect('nacelle.bearings_cost', 'tcc.bearings_cost')
        self.connect('nacelle.gearbox_cost', 'tcc.gearbox_cost')
        self.connect('nacelle.mechanicalBrakes_cost', 'tcc.mechanicalBrakes_cost')
        self.connect('nacelle.generator_cost', 'tcc.generator_cost')
        self.connect('nacelle.VSElectronics_cost', 'tcc.VSElectronics_cost')
        self.connect('nacelle.yawSystem_cost', 'tcc.yawSystem_cost')
        self.connect('nacelle.mainframeTotal_cost', 'tcc.mainframeTotal_cost')
        self.connect('nacelle.electronicCabling_cost', 'tcc.electronicCabling_cost')
        self.connect('nacelle.HVAC_cost', 'tcc.HVAC_cost')
        self.connect('nacelle.nacelleCover_cost', 'tcc.nacelleCover_cost')
        self.connect('nacelle.controls_cost', 'tcc.controls_cost')'''
        
        self.connect('tower.tower_mass', 'tcc.tower_mass')
        self.connect('tower.tower_cost', ['tcc.tower_cost','tower_cost'])

        self.connect('tcc.rotor_cost','rotor_cost')
        self.create_passthrough('tcc.turbine_mass')

    def execute(self):

        super(tcc_csm_assembly, self).execute()  # will actually run the workflow

#------------------------------------------------------------------
@implement_base(BaseTCCAggregator)
class tcc_csm_component(Component):

    # Variables    
    blade_cost = Float(0.0, units='USD', iotype='in', desc='cost for a single wind turbine blade')
    blade_mass = Float(0.0, units='kg', iotype='in', desc='mass for a single wind turbine blade')
    hub_system_cost = Float(0.0, units='USD', iotype='in', desc='hub system cost')
    hub_system_mass = Float(0.0, units='kg', iotype='in', desc='hub system mass')
    nacelle_mass = Float(0.0, units='kg', iotype='in', desc='nacelle mass')
    nacelle_cost = Float(0.0, units='USD', iotype='in', desc='nacelle cost')
    tower_cost = Float(0.0, units='USD', iotype='in', desc='cost for a tower')
    tower_mass = Float(0.0, units='kg', iotype='in', desc='mass for a turbine tower')

    # Parameters (and ignored inputs)
    blade_number = Int(3, iotype='in', desc = 'number of rotor blades')
    offshore = Bool(False, iotype='in', desc= 'boolean for offshore')

    '''hub_cost = Float(0.0, units='USD', iotype='in', desc='hub cost')
    hub_mass = Float(0.0, units='kg', iotype='in', desc='hub mass')
    pitch_system_cost = Float(0.0, units='USD', iotype='in', desc='pitch system cost')
    pitch_system_mass = Float(0.0, units='kg', iotype='in', desc='pitch system mass')
    spinner_cost = Float(0.0, units='USD', iotype='in', desc='spinner / nose cone cost')
    spinner_mass = Float(0.0, units='kg', iotype='in', desc='spinner / nose cone mass')

    lowSpeedShaft_mass = Float(0.0, units='kg', iotype='in', desc= 'low speed shaft mass')
    bearings_mass = Float(0.0, units='kg', iotype='in', desc= 'bearings system mass')
    gearbox_mass = Float(0.0, units='kg', iotype='in', desc= 'gearbox and housing mass')
    mechanicalBrakes_mass = Float(0.0, units='kg', iotype='in', desc= 'high speed shaft, coupling, and mechanical brakes mass')
    generator_mass = Float(0.0, units='kg', iotype='in', desc= 'generator and housing mass')
    VSElectronics_mass = Float(0.0, units='kg', iotype='in', desc= 'variable speed electronics mass')
    yawSystem_mass = Float(0.0, units='kg', iotype='in', desc= 'yaw system mass')
    mainframeTotal_mass = Float(0.0, units='kg', iotype='in', desc= 'mainframe total mass including bedplate')
    electronicCabling_mass = Float(0.0, units='kg', iotype='in', desc= 'electronic cabling mass')
    HVAC_mass = Float(0.0, units='kg', iotype='in', desc= 'HVAC system mass')
    nacelleCover_mass = Float(0.0, units='kg', iotype='in', desc= 'nacelle cover mass')
    controls_mass = Float(0.0, units='kg', iotype='in', desc= 'control system mass')

    lowSpeedShaft_cost = Float(0.0, units='kg', iotype='in', desc= 'low speed shaft _cost')
    bearings_cost = Float(0.0, units='kg', iotype='in', desc= 'bearings system _cost')
    gearbox_cost = Float(0.0, units='kg', iotype='in', desc= 'gearbox and housing _cost')
    mechanicalBrakes_cost = Float(0.0, units='kg', iotype='in', desc= 'high speed shaft, coupling, and mechanical brakes _cost')
    generator_cost = Float(0.0, units='kg', iotype='in', desc= 'generator and housing _cost')
    VSElectronics_cost = Float(0.0, units='kg', iotype='in', desc= 'variable speed electronics _cost')
    yawSystem_cost = Float(0.0, units='kg', iotype='in', desc= 'yaw system _cost')
    mainframeTotal_cost = Float(0.0, units='kg', iotype='in', desc= 'mainframe total _cost including bedplate')
    electronicCabling_cost = Float(0.0, units='kg', iotype='in', desc= 'electronic cabling _cost')
    HVAC_cost = Float(0.0, units='kg', iotype='in', desc= 'HVAC system _cost')
    nacelleCover_cost = Float(0.0, units='kg', iotype='in', desc= 'nacelle cover _cost')
    controls_cost = Float(0.0, units='kg', iotype='in', desc= 'control system _cost')'''

    # Outputs
    rotor_mass = Float(0.0, units='kg', iotype='out', desc='rotor mass')
    rotor_cost = Float(0.0, iotype='out', desc='rotor cost')
    turbine_mass = Float(0.0, units='kg', iotype='out', desc='turbine mass')
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

    def __init__(self):    

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
        """
        Execute Turbine Capital _costs Model of the NREL _cost and Scaling Model.
        """


        # high level output assignment
        self.rotor_mass = self.blade_mass * self.blade_number + self.hub_system_mass
        self.rotor_cost = self.blade_cost * self.blade_number + self.hub_system_cost
        self.turbine_mass = self.rotor_mass + self.nacelle_mass + self.tower_mass
        self.turbine_cost = self.rotor_cost + self.nacelle_cost + self.tower_cost

        if self.offshore:
            self.turbine_cost *= 1.1
   
        # derivatives     
        self.d_mass_d_blade_mass = self.blade_number
        self.d_mass_d_hub_mass = 1.0
        self.d_mass_d_nacelle_mass = 1.0
        self.d_mass_d_tower_mass = 1.0
        
        if self.offshore:
            self.d_cost_d_blade_cost = 1.1 * self.blade_number
            self.d_cost_d_hub_cost = 1.1
            self.d_cost_d_nacelle_cost = 1.1
            self.d_cost_d_tower_cost = 1.1
        else:
            self.d_cost_d_blade_cost = self.blade_number
            self.d_cost_d_hub_cost = 1.0
            self.d_cost_d_nacelle_cost = 1.0
            self.d_cost_d_tower_cost = 1.0

    def list_deriv_vars(self):

        inputs=['blade_mass', 'hub_system_mass', 'nacelle_mass', 'tower_mass', \
                'blade_cost', 'hub_system_cost', 'nacelle_cost', 'tower_cost']
        
        outputs = ['turbine_mass', 'turbine_cost']
        
        return inputs, outputs
        
    def provideJ(self):
        
        self.J = np.array([[self.d_mass_d_blade_mass, self.d_mass_d_hub_mass, self.d_mass_d_nacelle_mass, self.d_mass_d_tower_mass, 0.0, 0.0, 0.0, 0.0],\
                           [0.0, 0.0, 0.0, 0.0, self.d_cost_d_blade_cost, self.d_cost_d_hub_cost, self.d_cost_d_nacelle_cost, self.d_cost_d_tower_cost]])
        
        return self.J
  
#-----------------------------------------------------------------

def example_turbine():

    # simple test of module
    trb = tcc_csm_assembly()
    trb.rotor_diameter = 126.0
    trb.advanced_blade = True
    trb.blade_number = 3
    trb.hub_height = 90.0    
    trb.machine_rating = 5000.0
    trb.offshore = True
    trb.year = 2009
    trb.month = 12
    trb.drivetrain_design = 'geared'

    # Rotor force calculations for nacelle inputs
    maxTipSpd = 80.0
    maxEfficiency = 0.90201
    ratedWindSpd = 11.5064
    thrustCoeff = 0.50
    airDensity = 1.225

    ratedHubPower  = trb.machine_rating / maxEfficiency 
    rotorSpeed     = (maxTipSpd/(0.5*trb.rotor_diameter)) * (60.0 / (2*np.pi))
    trb.rotor_thrust  = airDensity * thrustCoeff * np.pi * trb.rotor_diameter**2 * (ratedWindSpd**2) / 8
    trb.rotor_torque = ratedHubPower/(rotorSpeed*(np.pi/30))*1000

    trb.run()
    
    print "The results for the NREL 5 MW Reference Turbine in an offshore 20 m water depth location are:"
    print "Overall turbine mass is {0:.2f} kg".format(trb.turbine_mass)
    print "Overall turbine cost is ${0:.2f} USD".format(trb.turbine_cost)

if __name__ == "__main__":

    example_turbine()
    
    #example_blade()
    
    #example_hub()
    
    #example_nacelle()
    
    #example_tower()