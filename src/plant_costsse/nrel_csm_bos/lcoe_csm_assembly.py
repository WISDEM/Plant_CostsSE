"""
LCOE_csm_ssembly.py
Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.api import IndepVarComp, Component, Problem, Group

# NREL cost and scaling model sub-assemblies
from nrel_csm_tcc import tcc_csm_fused
from nrel_csm_bos import bos_csm_fused
from nrel_csm_opex  import opex_csm_fused
from nrel_csm_fin import fin_csm_fused
from nrel_csm_aep import aep_csm_fused

def example():

    lcoe = lcoe_csm_assembly()

    # openmdao example of execution
    root = Group()
    root.add('bos_csm_test', FUSED_OpenMDAO(bos_csm_fused()), promotes=['*'])
    root.add('tcc_csm_test', FUSED_OpenMDAO(tcc_csm_fused()), promotes=['*'])
    root.add('fin_csm_test', FUSED_OpenMDAO(fin_csm_fused(fixed_charge_rate = 0.12, construction_finance_rate=0.0, tax_rate = 0.4, discount_rate = 0.07, \
                      construction_time = 1.0, project_lifetime = 20.0, sea_depth = 20.0)), promotes=['*'])
    prob = Problem(root)
    prob.setup()


    # set inputs
    # simple test of module
    # Turbine inputs
    prob['rotor_diameter'] = 126.0
    prob['blade_number'] = 3
    prob['hub_height'] = 90.0    
    prob['machine_rating'] = 5000.0

    # Rotor force calculations for nacelle inputs
    maxTipSpd = 80.0
    maxEfficiency = 0.90201
    ratedWindSpd = 11.5064
    thrustCoeff = 0.50
    airDensity = 1.225

    ratedHubPower  = prob['machine_rating'] / maxEfficiency 
    rotorSpeed     = (maxTipSpd/(0.5*prob['rotor_diameter'])) * (60.0 / (2*np.pi))
    prob['rotor_thrust']  = airDensity * thrustCoeff * np.pi * prob['rotor_diameter']**2 * (ratedWindSpd**2) / 8
    prob['rotor_torque'] = ratedHubPower/(rotorSpeed*(np.pi/30))*1000
    
    prob['year'] = 2009
    prob['month'] = 12

    # Finance, BOS and OPEX inputs
    prob['RNA_mass'] = 256634.5 # RNA mass is not used in this simple model
    prob['turbine_number'] = 100
    prob['sea_depth'] = 20.0
    prob['multiplier'] = 1.0

    prob.run()
    print("Overall cost of energy for an offshore wind plant with 100 NREL 5 MW turbines")
    for io in root.unknowns:
        print(io + ' ' + str(root.unknowns[io]))

if __name__=="__main__":

    example()
