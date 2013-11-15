#!/usr/bin/env python
# encoding: utf-8
"""
newBOS.py

Created by Andrew Ning on 2012-11-12.
Copyright (c) NREL. All rights reserved.
"""


def BOS(rating, diameter, hubHeight, nTurb, TCC, towerTopMass):
    """
    rating - turbine rating (kW)
    diameter - rotor diameter (m)
    hubHeight - rotor hub height (m)
    nTurb - number of turbines
    TCC - turbine capital cost ($)
    towerTopMass - tower top mass (kg)

    """

    TCC /= (rating*nTurb)  # convert to $/kW
    towerTopMass /= 1000  # convert to tonnes
    totalMW = rating*nTurb/1000.0


    # inputs from user
    # rating = 2300  # kW
    # diameter = 100  # m
    # hubHeight = 80  # m
    # nTurb = 87
    # TCC = 1286  # $/kW
    # towerTopMass = 160  # tonnes

    # other inputs
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
    mi = turbineTransportation
    if rating < 2500 and hubHeight < 100:
        turbineTransportCost = 1349*mi**0.746 * nTurb
    else:
        turbineTransportCost = 1867*mi**0.726 * nTurb




    # ---- engineering cost -------
    engineeringCost = 7188.5*nTurb

    multiplier = 16800
    if totalMW > 300:
        engineeringCost += 20*multiplier
    elif totalMW > 100:
        engineeringCost += 15*multiplier
    elif totalMW > 30:
        engineeringCost += 10*multiplier
    else:
        engineeringCost += 5*multiplier

    multiplier = 161675
    if totalMW > 200:
        engineeringCost += 2*multiplier
    else:
        engineeringCost += multiplier

    engineeringCost += 4000



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

    if hubHeight < 90:
        powerPerformanceCost += multiplier1 * 232600 + multiplier2 * 92600
    else:
        powerPerformanceCost += multiplier1 * 290000 + multiplier2 * 116800




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




    # ---- control - O&M building cost -----
    buildingCost = buildingSize*125 + 176125



    # ----- turbine foundation cost -----
    foundationCost = rating*diameter*towerTopMass/1000.0 + 163794*nTurb**-0.12683 \
        + (hubHeight-80)*500

    if soilCondition == 'Bouyant':
        foundationCost += 20000

    foundationCost *= nTurb



    # --- turbine erection cost ----
    erectionCost = (37*rating + 250000*nTurb**-0.41 + (hubHeight-80)*500) * nTurb \
        + 20000*windWeatherDelayDays + 35000*craneBreakdowns + 180*nTurb + 1800
    if deliveryAssistRequired:
        erectionCost += 60000 * nTurb



    # ----- collector substation costs -----
    collectorCost = 11652*(interconnectVoltage + totalMW) + 11795*totalMW**0.3549 + 1234300



    # ---- transmission line and interconnection cost -----
    transmissionCost = (1176*interconnectVoltage + 218257)*distanceToInterconnect**0.8937 \
        + 18115*interconnectVoltage + 165944



    # --- project management ----
    if constructionTime < 28:
        projMgtCost = (53.333*constructionTime**2 - 3442*constructionTime + 209542)*(constructionTime+2)
    else:
        projMgtCost = (constructionTime+2)*155000


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


    # ---- development cost ------
    developmentCost = developmentFee * 1e6


    # ------ total -----
    BOS = turbineTransportCost + insuranceCost + engineeringCost + powerPerformanceCost + \
        accessCost + siteSecurityCost + buildingCost + foundationCost + erectionCost + \
        electricalMaterialCost + electricalInstallationCost + collectorCost + \
        transmissionCost + projMgtCost + developmentCost


    # multiplier
    alpha = alpha_contingency + alpha_insurance

    BOS /= (1-alpha)

    # if needed
    contingencyCost = alpha_contingency*BOS
    insuranceCost += alpha_insurance*BOS

    return BOS
