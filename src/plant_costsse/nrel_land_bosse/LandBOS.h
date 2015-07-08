//
//  LandBOS.h
//  LandBOS
//
//  Created by Andrew Ning on 3/12/14.
//  Copyright (c) 2014 NREL. All rights reserved.
//

#ifndef __LANDBOS_H__
#define __LANDBOS_H__

#include <math.h>

typedef enum {FLAT_TO_ROLLING, RIDGE_TOP, MOUNTAINOUS} SiteTerrain;
typedef enum {SIMPLE, COMPLEX} TurbineLayout;
typedef enum {STANDARD, BOUYANT} SoilCondition;

typedef struct{
    double alpha;
    double cost;
} MultCost;


// Wind Farm Size (MW)
double farmSize(double rating, int nTurb);

// Construction Time (months)
int defaultConstructionTime(int nTurb);

// Access road entrances
int defaultAccessRoadEntrances(int nTurb);

// O&M Building Size (ft2)
double defaultBuildingSize(double farmSize);

// Quantity of Temporary Meteorological Towers for Testing
// (double returned so it can be used with smooth version)
double defaultTempMetTowers(double farmSize);

// Quantity of Permanent Meteorological Towers for Testing
// (double returned so it can be used with smooth version)
double defaultPermanentMetTowers(double farmSize);

// Wind/Weather delay days
int defaultWeatherDelayDays(int nTurb);

// Crane breakdowns
int defaultCraneBreakdowns(int nTurb);




double transportationCost(double tcc, double rating, int nTurb,
        double hubHt, double transportDist);

void deriv_transportationCost(double rating, int nTurb,
        double* dtcc, double* dhubHt);

double engineeringCost(int nTurb, double farmSize);

// (double accepted so it can be used with smooth version)
double powerPerformanceCost(double hubHt, double permanent,
        double temporary);

void deriv_powerPerformanceCost(double hubHt, double permanent,
        double temporary, double* dhubHt);

double accessRoadsCost(SiteTerrain terrain, TurbineLayout layout,
        int nTurb, double diameter, int constructionTime,
        int accessRoadEntrances);

void deriv_accessRoadsCost(SiteTerrain terrain, TurbineLayout layout,
        int nTurb, double *ddiameter);

double siteCompoundCost(int accessRoadEntrances, int constructionTime,
        double farmSize);

double buildingCost(double buildingSize);

double foundationCost(double rating, double diameter, double topMass,
        double hubHt, SoilCondition soil, int nTurb);

void deriv_foundationCost(double rating, double diameter, double topMass,
        int nTurb, double* ddiameter, double* dtopMass, double* dhubHt);

double erectionCost(double rating, double hubHt, int nTurb, int weatherDelayDays,
        int craneBreakdowns, int deliveryAssistRequired);

void deriv_erectionCost(int nTurb, double* dhubHt);

double electricalMaterialsCost(SiteTerrain terrain, TurbineLayout layout,
        double farmSize, double diameter, int nTurb, int padMountTransformer,
        double thermalBackfill);

void deriv_electricalMaterialsCost(SiteTerrain terrain, TurbineLayout layout,
        int nTurb, double* ddiameter);

double electricalInstallationCost(SiteTerrain terrain, TurbineLayout layout,
        double farmSize, double diameter, int nTurb,
        double rockTrenchingLength, double overheadCollector);

void deriv_electricalInstallationCost(SiteTerrain terrain, TurbineLayout layout,
        int nTurb, double rockTrenchingLength, double* ddiameter);

double substationCost(double voltage, double farmSize);

double transmissionCost(double voltage, double distInter,
        int newSwitchyardRequired);

double projectMgmtCost(int constructionTime);

double developmentCost(double developmentFee);

MultCost insuranceMultiplierAndCost(double tcc, double farmSize,
        double foundationCost, int performanceBond);

void deriv_insuranceMultiplierAndCost(double farmSize,
        int performanceBond, double* dtcc, double* dfoundationCost);

MultCost markupMultiplierAndCost(double transportationCost, double contingency,
        double warranty, double useTax, double overhead, double profitMargin);

void deriv_markupMultiplierAndCost(double contingency, double warranty,
        double useTax, double overhead, double profitMargin, double* dtransportationCost);

double totalCost(double rating, double diameter, double hubHt,
        int nTurb, double voltage, double distInter,
        SiteTerrain terrain, TurbineLayout layout, SoilCondition soil,
        double farmSize, double tcc, double topMass,
        int constructionTime, double buildingSize, double temporary,
        double permanent, int weatherDelayDays, int craneBreakdowns,
        int accessRoadEntrances,
        int deliveryAssistRequired, int padMountTransformer,
        int newSwitchyardRequired, double rockTrenchingLength,
        double thermalBackfill, double overheadCollector,
        int performanceBond, double contingency, double warranty,
        double useTax, double overhead, double profitMargin,
        double developmentFee, double transportDist);

#endif