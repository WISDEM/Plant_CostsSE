# distutils: language = c

cimport c_landbos



def farmSize(double rating, int nTurb):
    return c_landbos.farmSize(rating, nTurb)


def defaultConstructionTime(int nTurb):
    return c_landbos.defaultConstructionTime(nTurb)


def defaultAccessRoadEntrances(int nTurb):
    return c_landbos.defaultAccessRoadEntrances(nTurb)


def defaultBuildingSize(double farmSize):
    return c_landbos.defaultBuildingSize(farmSize)


def defaultTempMetTowers(double farmSize):
    return c_landbos.defaultTempMetTowers(farmSize)


def defaultPermanentMetTowers(double farmSize):
    return c_landbos.defaultPermanentMetTowers(farmSize)


def defaultWeatherDelayDays(int nTurb):
    return c_landbos.defaultWeatherDelayDays(nTurb)


def defaultCraneBreakdowns(int nTurb):
    return c_landbos.defaultCraneBreakdowns(nTurb)



def transportationCost(double tcc, double rating, int nTurb,
        double hubHt, double transportDist=0.0):
    return c_landbos.transportationCost(tcc, rating, nTurb, hubHt, transportDist)


def deriv_transportationCost(double rating, int nTurb):
    dtcc = 0.0
    dhubHt = 0.0
    c_landbos.deriv_transportationCost(rating, nTurb, &dtcc, &dhubHt)
    return dtcc, dhubHt


def engineeringCost(int nTurb, double farmSize):
    return c_landbos.engineeringCost(nTurb, farmSize)


def powerPerformanceCost(double hubHt, double permanent, double temporary):
    return c_landbos.powerPerformanceCost(hubHt, permanent, temporary)


def deriv_powerPerformanceCost(double hubHt, double permanent, double temporary):
    dhubHt = 0.0
    c_landbos.deriv_powerPerformanceCost(hubHt, permanent, temporary, &dhubHt)
    return dhubHt


def accessRoadsCost(c_landbos.SiteTerrain terrain, c_landbos.TurbineLayout layout,
        int nTurb, double diameter, int constructionTime, int accessRoadEntrances):
    return c_landbos.accessRoadsCost(terrain, layout,
        nTurb, diameter, constructionTime, accessRoadEntrances)


def deriv_accessRoadsCost(c_landbos.SiteTerrain terrain, c_landbos.TurbineLayout layout,
        int nTurb):
    ddiameter = 0.0
    c_landbos.deriv_accessRoadsCost(terrain, layout, nTurb, &ddiameter)
    return ddiameter


def siteCompoundCost(int accessRoadEntrances, int constructionTime, double farmSize):
    return c_landbos.siteCompoundCost(accessRoadEntrances, constructionTime, farmSize)


def buildingCost(double buildingSize):
    return c_landbos.buildingCost(buildingSize)


def foundationCost(double rating, double diameter, double topMass,
        double hubHt, c_landbos.SoilCondition soil, int nTurb):
    return c_landbos.foundationCost(rating, diameter, topMass,
        hubHt, soil, nTurb)


def deriv_foundationCost(double rating, double diameter, double topMass, int nTurb):

    ddiameter = 0.0
    dtopMass = 0.0
    dhubHt = 0.0
    c_landbos.deriv_foundationCost(rating, diameter, topMass, nTurb, &ddiameter, &dtopMass, &dhubHt)
    return ddiameter, dtopMass, dhubHt


def erectionCost(double rating, double hubHt, int nTurb, int weatherDelayDays,
        int craneBreakdowns, bint deliveryAssistRequired=False):
    return c_landbos.erectionCost(rating, hubHt, nTurb, weatherDelayDays,
        craneBreakdowns, deliveryAssistRequired)


def deriv_erectionCost(int nTurb):
    dhubHt = 0.0
    c_landbos.deriv_erectionCost(nTurb, &dhubHt)
    return dhubHt


def electricalMaterialsCost(c_landbos.SiteTerrain terrain, c_landbos.TurbineLayout layout,
        double farmSize, double diameter, int nTurb, bint padMountTransformer=True,
        double thermalBackfill=0.0):
    return c_landbos.electricalMaterialsCost(terrain, layout,
        farmSize, diameter, nTurb, padMountTransformer, thermalBackfill)


def deriv_electricalMaterialsCost(c_landbos.SiteTerrain terrain, c_landbos.TurbineLayout layout,
        int nTurb):
    ddiameter = 0.0
    c_landbos.deriv_electricalMaterialsCost(terrain, layout, nTurb, &ddiameter)
    return ddiameter


def electricalInstallationCost(c_landbos.SiteTerrain terrain, c_landbos.TurbineLayout layout,
        double farmSize, double diameter, int nTurb,
        double rockTrenchingLength=10.0, double overheadCollector=0.0):
    return c_landbos.electricalInstallationCost(terrain, layout,
        farmSize, diameter, nTurb, rockTrenchingLength, overheadCollector)


def deriv_electricalInstallationCost(c_landbos.SiteTerrain terrain, c_landbos.TurbineLayout layout,
        int nTurb, double rockTrenchingLength=10.0):
    ddiameter = 0.0
    c_landbos.deriv_electricalInstallationCost(terrain, layout,
        nTurb, rockTrenchingLength, &ddiameter)
    return ddiameter


def substationCost(double voltage, double farmSize):
    return c_landbos.substationCost(voltage, farmSize)


def transmissionCost(double voltage, double distInter,
        bint newSwitchyardRequired=True):
    return c_landbos.transmissionCost(voltage, distInter, newSwitchyardRequired)


def projectMgmtCost(int constructionTime):
    return c_landbos.projectMgmtCost(constructionTime)


def developmentCost(double developmentFee=5):
    return c_landbos.developmentCost(developmentFee)


def insuranceMultiplierAndCost(double tcc, double farmSize,
        double foundationCost, bint performanceBond=True):
    return c_landbos.insuranceMultiplierAndCost(tcc, farmSize,
        foundationCost, performanceBond)


def deriv_insuranceMultiplierAndCost(double farmSize, bint performanceBond=True):
    dtcc = 0.0
    dfoundationCost = 0.0
    c_landbos.deriv_insuranceMultiplierAndCost(farmSize, performanceBond,
        &dtcc, &dfoundationCost)
    return dtcc, dfoundationCost


def markupMultiplierAndCost(double transportationCost, double contingency=3.0,
        double warranty=0.02, double useTax=0.0, double overhead=5.0,
        double profitMargin=5.0):
    return c_landbos.markupMultiplierAndCost(transportationCost, contingency,
        warranty, useTax, overhead, profitMargin)


def deriv_markupMultiplierAndCost(double contingency=3.0,
        double warranty=0.02, double useTax=0.0, double overhead=5.0,
        double profitMargin=5.0):
    dtransportationCost = 0.0
    c_landbos.deriv_markupMultiplierAndCost(contingency, warranty,
        useTax, overhead, profitMargin, &dtransportationCost)
    return dtransportationCost


def totalCost(double rating, double diameter, double hubHt,
        int nTurb, double voltage, double distInter,
        c_landbos.SiteTerrain terrain, c_landbos.TurbineLayout layout,
        c_landbos.SoilCondition soil,
        double farmSize, double tcc, double topMass,
        int constructionTime, double buildingSize, double temporary,
        double permanent, int weatherDelayDays, int craneBreakdowns,
        int accessRoadEntrances,
        bint deliveryAssistRequired=False, bint padMountTransformer=True,
        bint newSwitchyardRequired=True, double rockTrenchingLength=10.0,
        double thermalBackfill=0.0, double overheadCollector=0.0,
        bint performanceBond=False, double contingency=3.0, double warranty=0.02,
        double useTax=0.0, double overhead=5.0, double profitMargin=5.0,
        double developmentFee=5.0, double transportDist=0.0):
    return c_landbos.totalCost(rating, diameter, hubHt,
        nTurb, voltage, distInter, terrain, layout, soil,
        farmSize, tcc, topMass, constructionTime, buildingSize,
        temporary, permanent, weatherDelayDays, craneBreakdowns,
        accessRoadEntrances, deliveryAssistRequired, padMountTransformer,
        newSwitchyardRequired, rockTrenchingLength, thermalBackfill,
        overheadCollector, performanceBond, contingency, warranty,
        useTax, overhead, profitMargin, developmentFee, transportDist)

