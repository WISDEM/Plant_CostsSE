"""
bos_nrel_onshore_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Str, Array, VarTree
import numpy as np

from fusedwind.plant_cost.fused_costs_asym import BOSVarTree, ExtendedBOSCostAggregator, ExtendedBOSCostModel

class bos_nrel_onshore_assembly(ExtendedBOSCostModel):

    def configure(self):

        super(bos_nrel_onshore_assembly, self).configure()
    
        self.replace('bos', bos_nrel_onshore_component())

class bos_nrel_onshore_component(ExtendedBOSCostAggregator):

    def __init__(self):

        super(bos_nrel_onshore_component, self).__init__()

    def execute(self):

        rating = self.machine_rating
        nTurb = self.turbine_number
        diameter = self.rotor_diameter
        hubHeight = self.hub_height
        towerTopMass = self.RNA_mass / 1000  # convert to tonnes
        TCC = self.turbine_cost / rating  # convert to $/kW
        totalMW = rating*nTurb/1000.0

        # other inputs (to be extracted later if desired)
        interconnectVoltage = 137  # kV
        distanceToInterconnect = 5  # mi
        siteTerrain = 'FlatToRolling'
        turbineLayout = 'Simple'
        soilCondition = 'Standard'
        constructionTime = 20  # months

        # advanced inputs
        deliveryAssistRequired = False
        buildingSize = 5000  # sqft
        windWeatherDelayDays = 80
        craneBreakdowns = 4
        accessRoadEntrances = 4
        performanceBond = False
        contingency = 3.0  # %
        warrantyManagement = 0.02  # %
        salesAndUseTax = 5  # %
        overhead = 6  # %
        profitMargin = 6  # %
        developmentFee = 5  # million
        turbineTransportation = 300  # miles

        # inputs that don't seem to be used
        # padMountTransformerRequired = True
        # rockTrenchingRequired = 10.0  # % of cable collector length
        # MVthermalBackfill = 0  # mi
        # MVoverheadCollector = 0  # mi


        # TODO: smoothness issues

        # ---- turbine and transport cost -----
        # mi = turbineTransportation
        # if rating < 2500 and hubHeight < 100:
        #     turbineTransportCost = 1349*mi**0.746 * nTurb
        # else:
        #     turbineTransportCost = 1867*mi**0.726 * nTurb

        # TODO: for now - my smoother version
        mi = turbineTransportation
        turbineTransportCost = 1867*mi**0.726 * nTurb
        self.BOS_breakdown.transportation_costs = turbineTransportCost

        # ---- engineering cost -------
        # engineeringCost = 7188.5*nTurb

        # multiplier = 16800
        # if totalMW > 300:
        #     engineeringCost += 20*multiplier
        # elif totalMW > 100:
        #     engineeringCost += 15*multiplier
        # elif totalMW > 30:
        #     engineeringCost += 10*multiplier
        # else:
        #     engineeringCost += 5*multiplier

        # multiplier = 161675
        # if totalMW > 200:
        #     engineeringCost += 2*multiplier
        # else:
        #     engineeringCost += multiplier

        # engineeringCost += 4000



        # TODO: for now - my smoother version
        engineeringCost = 7188.5*nTurb

        multiplier = 16800
        engineeringCost += 20*multiplier

        multiplier = 161675
        engineeringCost += 2*multiplier

        engineeringCost += 4000
        self.BOS_breakdown.development_costs = engineeringCost

        # ---- met mast and power performance engineering cost ----
        powerPerformanceCost = 200000

        if totalMW > 30:
            multiplier1 = 2
        else:
            multiplier1 = 1

        if totalMW > 100:
            multiplier2 = 4
        elif totalMW > 30:
            multiplier2 = 2
        else:
            multiplier2 = 1

        ## my smooth version (using cubic spline)
        hL = 85.0
        hU = 95.0

        poly1 = np.poly1d([-114.8, 30996.0, -2781030.0, 83175600.0])
        vL1 = 232600.0
        vU1 = 290000.0
        if hubHeight <= hL:
            value1 = vL1
            D1 = 0.0
        elif hubHeight >= hU:
            value1 = vU1
            D1 = 0.0
        else:
            value1 = poly1(hubHeight)
            D1 = poly1.deriv(1)(hubHeight)

        poly2 = np.poly1d([-48.4, 13068.0, -1172490.0, 35061600.0])
        vL2 = 92600
        vU2 = 116800

        if hubHeight <= hL:
            value2 = vL2
        elif hubHeight >= hU:
            value2 = vU2
        else:
            value2 = poly2(hubHeight)
            D2 = poly2.deriv(1)(hubHeight)

        powerPerformanceCost += multiplier1 * value1 + multiplier2 * value2
        self.BOS_breakdown.development_costs += powerPerformanceCost
        ppc_deriv = multiplier1 * D1 + multiplier2 * D2

        # if hubHeight < 90:
        #     powerPerformanceCost += multiplier1 * 232600 + multiplier2 * 92600
        # else:
        #     powerPerformanceCost += multiplier1 * 290000 + multiplier2 * 116800




        # --- access road and site improvement cost, and electrical costs -----
        if turbineLayout == 'Simple':
            if siteTerrain == 'FlatToRolling':
                accessCost = 5972082
                electricalMaterialCost = 10975731
                electricalInstallationCost = 4368309
            elif siteTerrain == 'RidgeTop':
                accessCost = 6891018
                electricalMaterialCost = 11439093
                electricalInstallationCost = 6427965
            elif siteTerrain == 'Mountainous':
                accessCost = 7484975
                electricalMaterialCost = 11465572
                electricalInstallationCost = 7594765
            else:
                print 'error'  # TODO: handle error
        elif turbineLayout == 'Complex':
            if siteTerrain == 'FlatToRolling':
                accessCost = 7187138
                electricalMaterialCost = 12229923
                electricalInstallationCost = 6400995
            elif siteTerrain == 'RidgeTop':
                accessCost = 8262300
                electricalMaterialCost = 12694155
                electricalInstallationCost = 9313885
            elif siteTerrain == 'Mountainous':
                accessCost = 9055930
                electricalMaterialCost = 12796728
                electricalInstallationCost = 10386160
            else:
                print 'error'  # TODO: handle error
        else:
            print 'error'  # TODO: handle error 
        self.BOS_breakdown.preparation_and_staging_costs = electricalInstallationCost + electricalMaterialCost + accessCost

        # ---- site compound and security costs -----
        siteSecurityCost = 9825*accessRoadEntrances + 29850*constructionTime

        if totalMW > 100:
            multiplier = 10
        elif totalMW > 30:
            multiplier = 5
        else:
            multiplier = 3

        siteSecurityCost += multiplier * 30000

        if totalMW > 30:
            siteSecurityCost += 90000

        siteSecurityCost += totalMW * 60 + 62400
        self.BOS_breakdown.preparation_and_staging_costs += siteSecurityCost

        # ---- control - O&M building cost -----
        buildingCost = buildingSize*125 + 176125
        self.BOS_breakdown.preparation_and_staging_costs += buildingCost

        # ----- turbine foundation cost -----
        foundationCost = rating*diameter*towerTopMass/1000.0 + 163794*nTurb**-0.12683 \
            + (hubHeight-80)*500

        if soilCondition == 'Bouyant':
            foundationCost += 20000

        foundationCost *= nTurb
        self.BOS_breakdown.foundation_and_substructure_costs = foundationCost

        # --- turbine erection cost ----
        erectionCost = (37*rating + 250000*nTurb**-0.41 + (hubHeight-80)*500) * nTurb \
            + 20000*windWeatherDelayDays + 35000*craneBreakdowns + 180*nTurb + 1800
        if deliveryAssistRequired:
            erectionCost += 60000 * nTurb
        self.BOS_breakdown.assembly_and_installation_costs = erectionCost

        # ----- collector substation costs -----
        collectorCost = 11652*(interconnectVoltage + totalMW) + 11795*totalMW**0.3549 + 1234300
        self.BOS_breakdown.electrical_costs = collectorCost

        # ---- transmission line and interconnection cost -----
        transmissionCost = (1176*interconnectVoltage + 218257)*distanceToInterconnect**0.8937 \
            + 18115*interconnectVoltage + 165944
        self.BOS_breakdown.electrical_costs += transmissionCost


        # --- project management ----
        if constructionTime < 28:
            projMgtCost = (53.333*constructionTime**2 - 3442*constructionTime + 209542)*(constructionTime+2)
        else:
            projMgtCost = (constructionTime+2)*155000
        self.BOS_breakdown.development_costs += projMgtCost

        # --- markup and contingency costs ----
        alpha_contingency = (contingency + warrantyManagement + salesAndUseTax + overhead + profitMargin)/100


        # ---- insurance bonds and permit costs -----
        insurance = (3.5 + 0.7 + 0.4 + 1.0) * TCC*totalMW
        if performanceBond:
            insurance += 10.0 * TCC*totalMW

        permit = foundationCost * 0.02
        permit += 20000

        insuranceCost = insurance + permit

        alpha_insurance = (3.5 + 0.7 + 0.4 + 1.0)/1000.0
        if performanceBond:
            alpha_insurance += 10.0/1000
        self.BOS_breakdown.soft_costs = alpha_contingency + alpha_insurance

        # ---- development cost ------
        developmentCost = developmentFee * 1e6
        self.BOS_breakdown.development_costs += developmentCost

        # ------ total -----
        self.bos_costs = turbineTransportCost + insuranceCost + engineeringCost + powerPerformanceCost + \
            accessCost + siteSecurityCost + buildingCost + foundationCost + erectionCost + \
            electricalMaterialCost + electricalInstallationCost + collectorCost + \
            transmissionCost + projMgtCost + developmentCost


        # multiplier
        alpha = alpha_contingency + alpha_insurance

        self.bos_costs /= (1-alpha)

        # # if needed
        # contingencyCost = alpha_contingency*BOS
        # insuranceCost += alpha_insurance*BOS

        # derivatives
        self.d_diameter = rating*towerTopMass/1000.0 * nTurb * (1 + 0.02)

        self.d_hubHeight = 500 * nTurb * (1 + 0.02) + 500 * nTurb + ppc_deriv

        self.d_TCC = (3.5 + 0.7 + 0.4 + 1.0)*totalMW
        if performanceBond:
            self.d_TCC += 10.0*totalMW
        self.d_TCC /= rating

        self.d_towerTopMass = rating*diameter/1000.0 * nTurb * (1 + 0.02)
        self.d_towerTopMass /= 1000

        self.d_mult = 1.0/(1-alpha)

    def linearize(self):

        # Jacobian        
        self.J = np.array([[self.d_mult * self.d_diameter, self.d_mult * self.d_hubHeight, \
                            self.d_mult * self.d_TCC, self.d_mult * self.d_towerTopMass]])

    def provideJ(self):

        inputs = ['rotor_diameter', 'hub_height', 'turbine_cost', 'RNA_mass']
        outputs = ['bos_costs']
 
        return inputs, outputs, self.J 

def example():

    bos = bos_nrel_onshore_assembly()
    bos.machine_rating = 5000.0
    bos.rotor_diameter = 126.0
    bos.turbine_cost = 5950209.283
    bos.turbine_number = 100
    bos.hub_height = 90.0
    bos.RNA_mass = 256634.5

    bos.execute()

    print "Cost {:.3f} found at ({:.2f}) turbines".format(bos.bos_costs, bos.turbine_number)
    
    #TODO: examples and main

if __name__ == "__main__":

    example()