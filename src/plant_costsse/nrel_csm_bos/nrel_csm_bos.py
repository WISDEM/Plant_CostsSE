"""
bos_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from fusedwind.plant_cost.fused_bos_costs import BOSVarTree, ExtendedBOSCostAggregator, ExtendedBOSCostModel, configure_extended_bos
from fusedwind.interface import implement_base

from commonse.config import *
import numpy as np

@implement_base(ExtendedBOSCostAggregator)
class bos_csm_component(Component):

    # Variables
    machine_rating = Float(iotype='in', units='kW', desc='turbine machine rating')
    rotor_diameter=Float(iotype='in', units='m', desc='rotor diameter')
    hub_height = Float(iotype='in', units='m', desc='hub height')
    RNA_mass = Float(iotype='in', units='kg', desc='Rotor Nacelle Assembly mass')
    turbine_cost = Float(iotype='in', units='USD', desc='Single Turbine Capital _costs')
    
    # Parameters
    turbine_number = Int(iotype='in', desc='number of turbines in project')
    sea_depth = Float(20.0, units = 'm', iotype = 'in', desc = 'sea depth for offshore wind plant')
    year = Int(2009, iotype='in', desc='year for project start')
    month = Int(12, iotype = 'in', desc= 'month for project start')
    multiplier = Float(1.0, iotype='in')

    # Outputs
    bos_breakdown = VarTree(BOSVarTree(), iotype='out', desc='BOS cost breakdown')
    bos_costs = Float(iotype='out', desc='Overall wind plant balance of station/system costs up to point of comissioning')

    def __init__(self):
        """
        OpenMDAO component to wrap BOS model of the NREL _cost and Scaling Model (csmBOS.py)

        """
        #super(bos_csm_component, self).__init__() #update for FUSED - not recognizing bos_csm_component super due to decorator
        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero' 

    def execute(self):
        """
        Executes BOS model of the NREL _cost and Scaling Model to estimate wind plant BOS costs.
        """

        # print "In {0}.execute()...".format(self.__class__)

        lPrmtsCostCoeff1 = 9.94E-04
        lPrmtsCostCoeff2 = 20.31
        oPrmtsCostFactor = 37.0 # $/kW (2003)
        scourCostFactor =  55.0 # $/kW (2003)
        ptstgCostFactor =  20.0 # $/kW (2003)
        ossElCostFactor = 260.0 # $/kW (2003) shallow
        ostElCostFactor = 290.0 # $/kW (2003) transitional
        ostSTransFactor  =  25.0 # $/kW (2003)
        ostTTransFactor  =  77.0 # $/kW (2003)
        osInstallFactor  = 100.0 # $/kW (2003) shallow & trans
        suppInstallFactor = 330.0 # $/kW (2003) trans additional
        paiCost         = 60000.0 # per turbine

        suretyBRate     = 0.03  # 3% of ICC
        suretyBond      = 0.0

        #set variables
        if self.sea_depth == 0:            # type of plant # 1: Land, 2: < 30m, 3: < 60m, 4: >= 60m
            iDepth = 1
        elif self.sea_depth < 30:
            iDepth = 2
        elif self.sea_depth < 60:
            iDepth = 3
        else:
            iDepth = 4

        # initialize self.ppi index calculator
        if iDepth == 1:
            ref_yr  = 2002
            ref_mon =    9
        else:
            ref_yr = 2003
            ref_mon = 9
        ppi.ref_yr = ref_yr
        ppi.ref_mon = ref_mon
        ppi.curr_yr = self.year
        ppi.curr_mon = self.month

        self.d_foundation_d_diameter = 0.0
        self.d_foundation_d_hheight = 0.0
        self.d_foundation_d_rating = 0.0
        # foundation costs
        if (iDepth == 1): # land
            fcCoeff = 303.23
            fcExp   = 0.4037
            SweptArea = (self.rotor_diameter*0.5)**2.0 * np.pi
            foundation_cost = fcCoeff * (self.hub_height*SweptArea)**fcExp
            fndnCostEscalator = ppi.compute('IPPI_FND')
            self.d_foundation_d_diameter = fndnCostEscalator * fcCoeff * fcExp * ((self.hub_height*(2.0 * 0.5 * (self.rotor_diameter * 0.5) * np.pi))**(fcExp-1)) * self.hub_height
            self.d_foundation_d_hheight = fndnCostEscalator * fcCoeff * fcExp * ((self.hub_height*SweptArea)**(fcExp-1)) * SweptArea
        elif (iDepth == 2):
            sscf = 300.0 # $/kW
            foundation_cost = sscf*self.machine_rating
            fndnCostEscalator = ppi.compute('IPPI_MPF')
            self.d_foundation_d_rating = fndnCostEscalator * sscf
        elif (iDepth == 3):
            sscf = 450.0 # $/kW
            foundation_cost = sscf*self.machine_rating
            fndnCostEscalator = ppi.compute('IPPI_OAI')
            self.d_foundation_d_rating = fndnCostEscalator * sscf
        elif (iDepth == 4):
            foundation_cost = 0.0
            fndnCostEscalator = 1.0

        foundation_cost *= fndnCostEscalator

        # cost calculations
        tpC1  =0.00001581
        tpC2  =-0.0375
        tpInt =54.7
        tFact = tpC1*self.machine_rating*self.machine_rating + tpC2*self.machine_rating + tpInt

        roadsCivil_costs = 0.0
        portStaging_costs = 0.0
        pai_costs = 0.0
        scour_costs = 0.0
        self.d_assembly_d_diameter = 0.0
        self.d_assembly_d_hheight = 0.0
        self.d_development_d_rating = 0.0
        self.d_preparation_d_rating = 0.0
        self.d_transport_d_rating = 0.0
        self.d_electrical_d_rating = 0.0
        self.d_assembly_d_rating = 0.0
        self.d_other_d_rating = 0.0
        if (iDepth == 1):
            engPermits_costs  = (lPrmtsCostCoeff1 * self.machine_rating * self.machine_rating) + \
                               (lPrmtsCostCoeff2 * self.machine_rating)
            ppi.ref_mon = 3
            engPermits_costs *= ppi.compute('IPPI_LPM')
            self.d_development_d_rating = ppi.compute('IPPI_LPM') * (2.0 * lPrmtsCostCoeff1 * self.machine_rating + lPrmtsCostCoeff2)
            ppi.ref_mon = 9

            elC1  = 3.49E-06
            elC2  = -0.0221
            elInt = 109.7
            eFact = elC1*self.machine_rating*self.machine_rating + elC2*self.machine_rating + elInt
            electrical_costs = self.machine_rating * eFact * ppi.compute('IPPI_LEL')
            self.d_electrical_d_rating = ppi.compute('IPPI_LEL') * (3. * elC1*self.machine_rating**2. + \
                                    2. * elC2*self.machine_rating + elInt)

            rcC1  = 2.17E-06
            rcC2  = -0.0145
            rcInt =69.54
            rFact = rcC1*self.machine_rating*self.machine_rating + rcC2*self.machine_rating + rcInt
            roadsCivil_costs = self.machine_rating * rFact * ppi.compute('IPPI_RDC')
            self.d_preparation_d_rating = ppi.compute('IPPI_RDC') * (3. * rcC1 * self.machine_rating**2. + \
                                     2. * rcC2 * self.machine_rating + rcInt)

            iCoeff = 1.965
            iExp   = 1.1736
            installation_costs = iCoeff * ((self.hub_height*self.rotor_diameter)**iExp) * ppi.compute('IPPI_LAI')
            self.d_assembly_d_diameter = iCoeff * ((self.hub_height*self.rotor_diameter)**(iExp-1)) * self.hub_height * ppi.compute('IPPI_LAI')
            self.d_assembly_d_hheight = iCoeff * ((self.hub_height*self.rotor_diameter)**(iExp-1)) * self.rotor_diameter * ppi.compute('IPPI_LAI')

            transportation_costs = self.machine_rating * tFact * ppi.compute('IPPI_TPT')
            self.d_transport_d_rating = ppi.compute('IPPI_TPT') * (tpC1* 3. * self.machine_rating**2. + \
                                   tpC2* 2. * self.machine_rating + tpInt )

        elif (iDepth == 2):  # offshore shallow
            ppi.ref_yr = 2003
            pai_costs            = paiCost * ppi.compute('IPPI_PAE')
            portStaging_costs    = ptstgCostFactor  * self.machine_rating * ppi.compute('IPPI_STP') # 1.415538133
            self.d_preparation_d_rating = ptstgCostFactor * ppi.compute('IPPI_STP')
            engPermits_costs     = oPrmtsCostFactor * self.machine_rating * ppi.compute('IPPI_OPM')
            self.d_development_d_rating = oPrmtsCostFactor * ppi.compute('IPPI_OPM')
            scour_costs         = scourCostFactor  * self.machine_rating * ppi.compute('IPPI_STP') # 1.415538133#
            self.d_other_d_rating = scourCostFactor  * ppi.compute('IPPI_STP')
            installation_costs   = osInstallFactor  * self.machine_rating * ppi.compute('IPPI_OAI')
            self.d_assembly_d_rating = osInstallFactor * ppi.compute('IPPI_OAI')
            electrical_costs     = ossElCostFactor  * self.machine_rating * ppi.compute('IPPI_OEL')
            self.d_electrical_d_rating = ossElCostFactor  * ppi.compute('IPPI_OEL')
            ppi.ref_yr  = 2002
            transportation_costs = self.machine_rating * tFact * ppi.compute('IPPI_TPT')
            self.d_transport_d_rating = ppi.compute('IPPI_TPT') * (tpC1* 3. * self.machine_rating**2. + \
                                   tpC2* 2. * self.machine_rating + tpInt )
            ppi.ref_yr = 2003

        elif (iDepth == 3):  # offshore transitional depth
            ppi.ref_yr = 2003
            turbInstall   = osInstallFactor  * self.machine_rating * ppi.compute('IPPI_OAI')
            supportInstall = suppInstallFactor * self.machine_rating * ppi.compute('IPPI_OAI')
            installation_costs = turbInstall + supportInstall
            self.d_assembly_d_rating = (osInstallFactor + suppInstallFactor) * ppi.compute('IPPI_OAI')
            pai_costs          = paiCost                          * ppi.compute('IPPI_PAE')
            electrical_costs     = ostElCostFactor  * self.machine_rating * ppi.compute('IPPI_OEL')
            self.d_electrical_d_rating = ossElCostFactor  * ppi.compute('IPPI_OEL')
            portStaging_costs   = ptstgCostFactor  * self.machine_rating * ppi.compute('IPPI_STP')
            self.d_preparation_d_rating = ptstgCostFactor * ppi.compute('IPPI_STP')
            engPermits_costs     = oPrmtsCostFactor * self.machine_rating * ppi.compute('IPPI_OPM')
            self.d_development_d_rating = oPrmtsCostFactor * ppi.compute('IPPI_OPM')
            scour_costs          = scourCostFactor  * self.machine_rating * ppi.compute('IPPI_STP')
            self.d_other_d_rating = scourCostFactor * ppi.compute('IPPI_STP')
            ppi.ref_yr  = 2002
            turbTrans           = ostTTransFactor  * self.machine_rating * ppi.compute('IPPI_TPT')
            self.d_transport_d_rating = ostTTransFactor  * ppi.compute('IPPI_TPT')
            ppi.ref_yr = 2003
            supportTrans        = ostSTransFactor  * self.machine_rating * ppi.compute('IPPI_OAI')
            transportation_costs = self.turbTrans + self.supportTrans
            self.d_transport_d_rating += ostSTransFactor  * ppi.compute('IPPI_OAI')

        elif (iDepth == 4):  # offshore deep
            print "\ncsmBOS: Add costCat 4 code\n\n"

        bos_costs = foundation_cost + \
                    transportation_costs + \
                    roadsCivil_costs    + \
                    portStaging_costs   + \
                    installation_costs   + \
                    electrical_costs     + \
                    engPermits_costs    + \
                    pai_costs          + \
                    scour_costs

        self.d_other_d_tcc = 0.0
        if (self.sea_depth > 0.0):
            suretyBond = suretyBRate * (self.turbine_cost + bos_costs)
            self.d_other_d_tcc = suretyBRate
            d_surety_d_rating = suretyBRate * (self.d_development_d_rating + self.d_preparation_d_rating + self.d_transport_d_rating + \
                          self.d_foundation_d_rating + self.d_electrical_d_rating + self.d_assembly_d_rating + self.d_other_d_rating)
            self.d_other_d_rating += d_surety_d_rating
        else:
            suretyBond = 0.0

        self.bos_costs = self.turbine_number * (bos_costs + suretyBond)
        self.bos_costs *= self.multiplier  # TODO: add to gradients

        self.bos_breakdown.development_costs = engPermits_costs * self.turbine_number
        self.bos_breakdown.preparation_and_staging_costs = (roadsCivil_costs + portStaging_costs) * self.turbine_number
        self.bos_breakdown.transportation_costs = (transportation_costs * self.turbine_number)
        self.bos_breakdown.foundation_and_substructure_costs = foundation_cost * self.turbine_number
        self.bos_breakdown.electrical_costs = electrical_costs * self.turbine_number
        self.bos_breakdown.assembly_and_installation_costs = installation_costs * self.turbine_number
        self.bos_breakdown.soft_costs = 0.0
        self.bos_breakdown.other_costs = (pai_costs + scour_costs + suretyBond) * self.turbine_number
  
        # derivatives
        self.d_development_d_rating *= self.turbine_number
        self.d_preparation_d_rating *= self.turbine_number
        self.d_transport_d_rating *= self.turbine_number
        self.d_foundation_d_rating *= self.turbine_number
        self.d_electrical_d_rating *= self.turbine_number
        self.d_assembly_d_rating *= self.turbine_number
        self.d_soft_d_rating = 0.0
        self.d_other_d_rating *= self.turbine_number
        self.d_cost_d_rating = self.d_development_d_rating + self.d_preparation_d_rating + self.d_transport_d_rating + \
                          self.d_foundation_d_rating + self.d_electrical_d_rating + self.d_assembly_d_rating + \
                          self.d_soft_d_rating + self.d_other_d_rating

        self.d_development_d_diameter = 0.0
        self.d_preparation_d_diameter = 0.0
        self.d_transport_d_diameter = 0.0
        #self.d_foundation_d_diameter
        self.d_electrical_d_diameter = 0.0
        #self.d_assembly_d_diameter
        self.d_soft_d_diameter = 0.0
        self.d_other_d_diameter = 0.0
        self.d_cost_d_diameter = self.d_development_d_diameter + self.d_preparation_d_diameter + self.d_transport_d_diameter + \
                          self.d_foundation_d_diameter + self.d_electrical_d_diameter + self.d_assembly_d_diameter + \
                          self.d_soft_d_diameter + self.d_other_d_diameter

        self.d_development_d_tcc = 0.0
        self.d_preparation_d_tcc = 0.0
        self.d_transport_d_tcc = 0.0
        self.d_foundation_d_tcc = 0.0
        self.d_electrical_d_tcc = 0.0
        self.d_assembly_d_tcc = 0.0
        self.d_soft_d_tcc = 0.0
        self.d_other_d_tcc *= self.turbine_number
        self.d_cost_d_tcc = self.d_development_d_tcc + self.d_preparation_d_tcc + self.d_transport_d_tcc + \
                          self.d_foundation_d_tcc + self.d_electrical_d_tcc + self.d_assembly_d_tcc + \
                          self.d_soft_d_tcc + self.d_other_d_tcc

        self.d_development_d_hheight = 0.0
        self.d_preparation_d_hheight = 0.0
        self.d_transport_d_hheight = 0.0
        #self.d_foundation_d_hheight
        self.d_electrical_d_hheight = 0.0
        #self.d_assembly_d_hheight
        self.d_soft_d_hheight = 0.0
        self.d_other_d_hheight = 0.0
        self.d_cost_d_hheight = self.d_development_d_hheight + self.d_preparation_d_hheight + self.d_transport_d_hheight + \
                          self.d_foundation_d_hheight + self.d_electrical_d_hheight + self.d_assembly_d_hheight + \
                          self.d_soft_d_hheight + self.d_other_d_hheight

        self.d_development_d_rna = 0.0
        self.d_preparation_d_rna = 0.0
        self.d_transport_d_rna = 0.0
        self.d_foundation_d_rna = 0.0
        self.d_electrical_d_rna = 0.0
        self.d_assembly_d_rna = 0.0
        self.d_soft_d_rna = 0.0
        self.d_other_d_rna = 0.0
        self.d_cost_d_rna = self.d_development_d_rna + self.d_preparation_d_rna + self.d_transport_d_rna + \
                          self.d_foundation_d_rna + self.d_electrical_d_rna + self.d_assembly_d_rna + \
                          self.d_soft_d_rna + self.d_other_d_rna

    def list_deriv_vars(self):

        inputs = ['machine_rating', 'rotor_diameter', 'turbine_cost', 'hub_height', 'RNA_mass']
        outputs = ['bos_breakdown.development_costs', 'bos_breakdown.preparation_and_staging_costs',\
                   'bos_breakdown.transportation_costs', 'bos_breakdown.foundation_and_substructure_costs',\
                   'bos_breakdown.electrical_costs', 'bos_breakdown.assembly_and_installation_costs',\
                   'bos_breakdown.soft_costs', 'bos_breakdown.other_costs', 'bos_costs']

        return inputs, outputs

    def provideJ(self):

        self.J = np.array([[self.d_development_d_rating, self.d_development_d_diameter, self.d_development_d_tcc, self.d_development_d_hheight, self.d_development_d_rna],\
                           [self.d_preparation_d_rating, self.d_preparation_d_diameter, self.d_preparation_d_tcc, self.d_preparation_d_hheight, self.d_preparation_d_rna],\
                           [self.d_transport_d_rating, self.d_transport_d_diameter, self.d_transport_d_tcc, self.d_transport_d_hheight, self.d_transport_d_rna],\
                           [self.d_foundation_d_rating, self.d_foundation_d_diameter, self.d_foundation_d_tcc, self.d_foundation_d_hheight, self.d_foundation_d_rna],\
                           [self.d_electrical_d_rating, self.d_electrical_d_diameter, self.d_electrical_d_tcc, self.d_electrical_d_hheight, self.d_electrical_d_rna],\
                           [self.d_assembly_d_rating, self.d_assembly_d_diameter, self.d_assembly_d_tcc, self.d_assembly_d_hheight, self.d_assembly_d_rna],\
                           [self.d_soft_d_rating, self.d_soft_d_diameter, self.d_soft_d_tcc, self.d_soft_d_hheight, self.d_soft_d_rna],\
                           [self.d_other_d_rating, self.d_other_d_diameter, self.d_other_d_tcc, self.d_other_d_hheight, self.d_other_d_rna],\
                           [self.d_cost_d_rating, self.d_cost_d_diameter, self.d_cost_d_tcc, self.d_cost_d_hheight, self.d_cost_d_rna]])

        return self.J


@implement_base(ExtendedBOSCostModel)
class bos_csm_assembly(Assembly):

    # Variables
    machine_rating = Float(iotype='in', units='kW', desc='turbine machine rating')
    rotor_diameter=Float(iotype='in', units='m', desc='rotor diameter')
    hub_height = Float(iotype='in', units='m', desc='hub height')
    RNA_mass = Float(iotype='in', units='kg', desc='Rotor Nacelle Assembly mass')
    turbine_cost = Float(iotype='in', units='USD', desc='Single Turbine Capital _costs')
    
    # Parameters
    turbine_number = Int(iotype='in', desc='number of turbines in project')
    sea_depth = Float(20.0, units = 'm', iotype = 'in', desc = 'sea depth for offshore wind plant')
    year = Int(2009, iotype='in', desc='year for project start')
    month = Int(12, iotype = 'in', desc= 'month for project start')
    multiplier = Float(1.0, iotype='in')

    # Outputs
    bos_breakdown = VarTree(BOSVarTree(), iotype='out', desc='BOS cost breakdown')
    bos_costs = Float(iotype='out', desc='Overall wind plant balance of station/system costs up to point of comissioning')

    def configure(self):

        super(bos_csm_assembly, self).configure()

        configure_extended_bos(self)
        
        self.replace('bos',bos_csm_component())

        self.connect('machine_rating','bos.machine_rating')
        self.connect('rotor_diameter','bos.rotor_diameter')
        self.connect('hub_height','bos.hub_height')
        self.connect('RNA_mass','bos.RNA_mass')
        self.connect('turbine_cost','bos.turbine_cost')
        self.connect('turbine_number','bos.turbine_number')
        self.connect('sea_depth','bos.sea_depth')
        self.connect('year','bos.year')
        self.connect('month','bos.month')
        self.connect('multiplier','bos.multiplier')

#-----------------------------------------------------------------

def example():

    # simple test of module
    bos = bos_csm_assembly()
    bos.machine_rating = 5000.0
    bos.rotor_diameter = 126.0
    bos.turbine_cost = 5950209.28
    bos.hub_height = 90.0
    bos.RNA_mass = 256634.5 # RNA mass is not used in this simple model
    bos.turbine_number = 100
    bos.sea_depth = 20.0
    bos.year = 2009
    bos.month = 12
    bos.multiplier = 1.0

    bos.run()
    print "Balance of Station Costs for an offshore wind plant with 100 NREL 5 MW turbines"
    print "BOS cost offshore: ${0:.2f} USD".format(bos.bos_costs)
    print "BOS cost per turbine: ${0:.2f} USD".format(bos.bos_costs / bos.turbine_number)
    print

    bos.sea_depth = 0.0
    bos.turbine_cost = 5229222.77

    bos.run()
    print "Balance of Station Costs for an land-based wind plant with 100 NREL 5 MW turbines"
    print "BOS cost land-based: ${0:.2f} USD".format(bos.bos_costs)
    print "BOS cost per turbine: ${0:.2f} USD".format(bos.bos_costs / bos.turbine_number)
    print

if __name__ == "__main__":

    example()