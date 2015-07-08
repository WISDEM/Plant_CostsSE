#!/usr/bin/env python
# encoding: utf-8
"""
LandBOS.py

Created by Andrew Ning on 2014-03-12.
Copyright (c) NREL. All rights reserved.
"""

import numpy as np
from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Int, Float, Enum, Bool

import _landbos


def Enum2Int(component, trait):
    return component.get_trait(trait).values.index(getattr(component, trait))


class FarmSize(Component):

    rating = Float(iotype='in', units='kW', desc='machine rating')
    nTurbines = Int(iotype='in', desc='number of turbines')

    farmSize = Float(iotype='out', units='MW', desc='wind farm size')

    def execute(self):
        self.farmSize = _landbos.farmSize(self.rating, self.nTurbines)


class Defaults(Component):

    nTurbines = Int(iotype='in', desc='number of turbines')
    farmSize = Float(iotype='in', units='MW', desc='wind farm size')
    override_constructionTime = Int(-1, iotype='in', units='mo', desc='construction time')
    override_accessRoadEntrances = Int(-1, iotype='in', desc='access road entrances')
    override_weatherDelayDays = Int(-1, iotype='in', units='d', desc='weather delay days')
    override_craneBreakdowns = Int(-1, iotype='in', desc='crane breakdowns')
    override_buildingSize = Float(-1, iotype='in', units='ft**2', desc='O&M building size')
    override_permanentMetTowers = Float(-1, iotype='in', desc='permananet meteorological towers')
    override_tempMetTowers = Float(-1, iotype='in', desc='temporary meteorological towers')

    constructionTime = Int(iotype='out', units='mo', desc='construction time')
    accessRoadEntrances = Int(iotype='out', desc='access road entrances')
    weatherDelayDays = Int(iotype='out', units='d', desc='weather delay days')
    craneBreakdowns = Int(iotype='out', desc='crane breakdowns')
    buildingSize = Float(iotype='in', units='ft**2', desc='O&M building size')
    permanentMetTowers = Float(iotype='in', desc='permananet meteorological towers')
    tempMetTowers = Float(iotype='in', desc='temporary meteorological towers')

    def execute(self):
        if self.override_constructionTime == -1:
            self.constructionTime = _landbos.defaultConstructionTime(self.nTurbines)
        else:
            self.constructionTime = self.override_constructionTime

        if self.override_accessRoadEntrances == -1:
            self.accessRoadEntrances = _landbos.defaultAccessRoadEntrances(self.nTurbines)
        else:
            self.accessRoadEntrances = self.override_accessRoadEntrances

        if self.override_weatherDelayDays == -1:
            self.weatherDelayDays = _landbos.defaultWeatherDelayDays(self.nTurbines)
        else:
            self.weatherDelayDays = self.override_weatherDelayDays

        if self.override_craneBreakdowns == -1:
            self.craneBreakdowns = _landbos.defaultCraneBreakdowns(self.nTurbines)
        else:
            self.craneBreakdowns = self.override_craneBreakdowns

        if self.override_buildingSize == -1:
            self.buildingSize = _landbos.defaultBuildingSize(self.farmSize)
        else:
            self.buildingSize = self.override_buildingSize

        if self.override_permanentMetTowers == -1:
            self.permanentMetTowers = _landbos.defaultPermanentMetTowers(self.farmSize)
        else:
            self.permanentMetTowers = self.override_permanentMetTowers

        if self.override_tempMetTowers == -1:
            self.tempMetTowers = _landbos.defaultTempMetTowers(self.farmSize)
        else:
            self.tempMetTowers = self.override_tempMetTowers




class Transportation(Component):

    TCC = Float(iotype='in', units='USD/kW', desc='turbine capital cost per kW')
    rating = Float(iotype='in', units='kW', desc='machine rating')
    nTurbines = Int(iotype='in', desc='number of turbines')
    hubHeight = Float(iotype='in', units='m', desc='hub height')
    transportDist = Float(iotype='in', units='mi', desc='transportation distance')

    cost = Float(iotype='out', units='USD', desc='turbine and transportation cost')

    def execute(self):
        self.cost = _landbos.transportationCost(self.TCC, self.rating,
            self.nTurbines, self.hubHeight, self.transportDist)

    def list_deriv_vars(self):

        inputs = ('TCC', 'hubHeight')
        outputs = ('cost',)

        return inputs, outputs

    def provideJ(self):

        dtcc, dhubHt = _landbos.deriv_transportationCost(self.rating, self.nTurbines)
        J = np.array([[dtcc, dhubHt]])

        return J


class Engineering(Component):

    nTurbines = Int(iotype='in', desc='number of turbines')
    farmSize = Float(iotype='in', units='MW', desc='wind farm size')

    cost = Float(iotype='out', units='USD', desc='engineering cost')

    def execute(self):
        self.cost = _landbos.engineeringCost(self.nTurbines, self.farmSize)


class PowerPerformance(Component):

    hubHeight = Float(iotype='in', units='m', desc='hub height')
    permanentMetTowers = Float(iotype='in', desc='permananet meteorological towers')
    tempMetTowers = Float(iotype='in', desc='temporary meteorological towers')

    cost = Float(iotype='out', units='USD', desc='met masts and power performance cost')

    def execute(self):
        self.cost = _landbos.powerPerformanceCost(self.hubHeight,
            self.permanentMetTowers, self.tempMetTowers)

    def list_deriv_vars(self):

        inputs = ('hubHeight',)
        outputs = ('cost',)

        return inputs, outputs

    def provideJ(self):

        dhubHT = _landbos.deriv_powerPerformanceCost(self.hubHeight, self.permanentMetTowers, self.tempMetTowers)
        J = np.array([[dhubHT]])

        return J


class AccessRoads(Component):

    terrain = Enum('FLAT_TO_ROLLING', ('FLAT_TO_ROLLING', 'RIDGE_TOP', 'MOUNTAINOUS'),
        iotype='in', desc='terrain options')
    layout = Enum('SIMPLE', ('SIMPLE', 'COMPLEX'), iotype='in',
        desc='layout options')
    nTurbines = Int(iotype='in', desc='number of turbines')
    diameter = Float(iotype='in', units='m', desc='rotor diameter')
    constructionTime = Int(iotype='in', units='mo', desc='construction time')
    accessRoadEntrances = Int(iotype='in', desc='access road entrances')

    cost = Float(iotype='out', units='USD', desc='access roads and site improvement cost')

    def execute(self):
        self.cost = _landbos.accessRoadsCost(Enum2Int(self, 'terrain'),
            Enum2Int(self, 'layout'), self.nTurbines, self.diameter,
            self.constructionTime, self.accessRoadEntrances)

    def list_deriv_vars(self):

        inputs = ('diameter',)
        outputs = ('cost',)

        return inputs, outputs

    def provideJ(self):

        ddiameter = _landbos.deriv_accessRoadsCost(Enum2Int(self, 'terrain'),
            Enum2Int(self, 'layout'), self.nTurbines)
        J = np.array([[ddiameter]])

        return J


class SiteCompound(Component):

    constructionTime = Int(iotype='in', units='mo', desc='construction time')
    accessRoadEntrances = Int(iotype='in', desc='access road entrances')
    farmSize = Float(iotype='in', units='MW', desc='wind farm size')

    cost = Float(iotype='out', units='USD', desc='site compound and security cost')

    def execute(self):
        self.cost = _landbos.siteCompoundCost(self.accessRoadEntrances,
            self.constructionTime, self.farmSize)


class Building(Component):

    buildingSize = Float(iotype='in', units='ft**2', desc='O&M building size')

    cost = Float(iotype='out', units='USD', desc='control - O&M building cost')

    def execute(self):
        self.cost = _landbos.buildingCost(self.buildingSize)


class Foundations(Component):

    rating = Float(iotype='in', units='kW', desc='machine rating')
    diameter = Float(iotype='in', units='m', desc='rotor diameter')
    topMass = Float(iotype='in', units='kg', desc='tower top mass (tonnes)')
    hubHeight = Float(iotype='in', units='m', desc='hub height')
    soil = Enum('STANDARD', ('STANDARD', 'BOUYANT'), iotype='in',
        desc='soil options')
    nTurbines = Int(iotype='in', desc='number of turbines')

    cost = Float(iotype='out', units='USD', desc='foundations cost')

    def execute(self):
        self.cost = _landbos.foundationCost(self.rating, self.diameter,
            self.topMass/1000.0, self.hubHeight, Enum2Int(self, 'soil'), self.nTurbines)

    def list_deriv_vars(self):

        inputs = ('diameter', 'topMass', 'hubHeight')
        outputs = ('cost',)

        return inputs, outputs

    def provideJ(self):

        ddiameter, dtopMass, dhubHt = _landbos.deriv_foundationCost(self.rating,
            self.diameter, self.topMass/1000.0, self.nTurbines)

        J = np.array([[ddiameter, dtopMass/1000.0, dhubHt]])

        return J


class Erection(Component):

    rating = Float(iotype='in', units='kW', desc='machine rating')
    hubHeight = Float(iotype='in', units='m', desc='hub height')
    nTurbines = Int(iotype='in', desc='number of turbines')
    weatherDelayDays = Int(iotype='in', units='d', desc='weather delay days')
    craneBreakdowns = Int(iotype='in', desc='crane breakdowns')
    deliveryAssistRequired = Bool(iotype='in', desc='delivery assist required')

    cost = Float(iotype='out', units='USD', desc='erection cost')

    def execute(self):
        self.cost = _landbos.erectionCost(self.rating, self.hubHeight,
            self.nTurbines, self.weatherDelayDays,
            self.craneBreakdowns, self.deliveryAssistRequired)

    def list_deriv_vars(self):

        inputs = ('hubHeight',)
        outputs = ('cost',)

        return inputs, outputs

    def provideJ(self):

        dhubHt = _landbos.deriv_erectionCost(self.nTurbines)
        J = np.array([[dhubHt]])

        return J


class ElecMaterials(Component):

    terrain = Enum('FLAT_TO_ROLLING', ('FLAT_TO_ROLLING', 'RIDGE_TOP', 'MOUNTAINOUS'),
        iotype='in', desc='terrain options')
    layout = Enum('SIMPLE', ('SIMPLE', 'COMPLEX'), iotype='in',
        desc='layout options')
    farmSize = Float(iotype='in', units='MW', desc='wind farm size')
    diameter = Float(iotype='in', units='m', desc='rotor diameter')
    nTurbines = Int(iotype='in', desc='number of turbines')
    padMountTransformer = Bool(True, iotype='in', desc='pad mount transformer required')
    thermalBackfill = Float(0.0, iotype='in', units='mi', desc='MV thermal backfill')

    cost = Float(iotype='out', units='USD', desc='MV electrical materials cost')

    def execute(self):
        self.cost = _landbos.electricalMaterialsCost(Enum2Int(self, 'terrain'),
            Enum2Int(self, 'layout'), self.farmSize, self.diameter, self.nTurbines,
            self.padMountTransformer, self.thermalBackfill)

    def list_deriv_vars(self):

        inputs = ('diameter',)
        outputs = ('cost',)

        return inputs, outputs

    def provideJ(self):

        ddiameter = _landbos.deriv_electricalMaterialsCost(Enum2Int(self, 'terrain'),
            Enum2Int(self, 'layout'), self.nTurbines)
        J = np.array([[ddiameter]])

        return J


class ElecInstallation(Component):

    terrain = Enum('FLAT_TO_ROLLING', ('FLAT_TO_ROLLING', 'RIDGE_TOP', 'MOUNTAINOUS'),
        iotype='in', desc='terrain options')
    layout = Enum('SIMPLE', ('SIMPLE', 'COMPLEX'), iotype='in',
        desc='layout options')
    farmSize = Float(iotype='in', units='MW', desc='wind farm size')
    diameter = Float(iotype='in', units='m', desc='rotor diameter')
    nTurbines = Int(iotype='in', desc='number of turbines')
    rockTrenchingLength = Float(10.0, iotype='in', desc='rock trenching required (% of collector cable length)')
    overheadCollector = Float(0.0, iotype='in', units='mi', desc='MV overhead collector')

    cost = Float(iotype='out', units='USD', desc='MV electrical materials cost')

    def execute(self):
        self.cost = _landbos.electricalInstallationCost(Enum2Int(self, 'terrain'),
            Enum2Int(self, 'layout'), self.farmSize, self.diameter, self.nTurbines,
            self.rockTrenchingLength, self.overheadCollector)

    def list_deriv_vars(self):

        inputs = ('diameter',)
        outputs = ('cost',)

        return inputs, outputs

    def provideJ(self):

        ddiameter = _landbos.deriv_electricalInstallationCost(Enum2Int(self, 'terrain'),
            Enum2Int(self, 'layout'), self.nTurbines, self.rockTrenchingLength)
        J = np.array([[ddiameter]])

        return J


class Substation(Component):

    voltage = Float(iotype='in', units='kV', desc='interconnect voltage')
    farmSize = Float(iotype='in', units='MW', desc='wind farm size')

    cost = Float(iotype='out', units='USD', desc='collector substation cost')

    def execute(self):
        self.cost = _landbos.substationCost(self.voltage, self.farmSize)


class Transmission(Component):

    voltage = Float(iotype='in', units='kV', desc='interconnect voltage')
    distInter = Float(iotype='in', units='mi', desc='distance to interconnect')
    newSwitchyardRequired = Bool(True, iotype='in', desc='new switchyard required')

    cost = Float(iotype='out', units='USD', desc='transmission line and interconnect cost')

    def execute(self):
        self.cost = _landbos.transmissionCost(self.voltage, self.distInter,
            self.newSwitchyardRequired)


class ProjectMgmt(Component):

    constructionTime = Int(iotype='in', units='mo', desc='construction time')

    cost = Float(iotype='out', units='USD', desc='project management cost')

    def execute(self):
        self.cost = _landbos.projectMgmtCost(self.constructionTime)


class Development(Component):

    developmentFee = Float(5.0, iotype='in', desc='development fee (in millions of dollars)')

    cost = Float(iotype='out', units='USD', desc='development cost')

    def execute(self):
        self.cost = _landbos.developmentCost(self.developmentFee)


class Insurance(Component):

    TCC = Float(iotype='in', units='USD/kW', desc='turbine capital cost per kW')
    farmSize = Float(iotype='in', units='MW', desc='wind farm size')
    foundationCost = Float(iotype='in', units='USD', desc='foundation cost')
    performanceBond = Bool(False, iotype='in', desc='performance bond')

    alpha = Float(iotype='out', desc='multiplier portion of insurance cost')
    cost = Float(iotype='out', units='USD', desc='constant portion of insurance cost')

    def execute(self):
        values = _landbos.insuranceMultiplierAndCost(self.TCC, self.farmSize,
        self.foundationCost, self.performanceBond)
        self.alpha = values['alpha']
        self.cost = values['cost']

    def list_deriv_vars(self):

        inputs = ('TCC', 'foundationCost')
        outputs = ('alpha', 'cost')

        return inputs, outputs

    def provideJ(self):

        dtcc, dfoundationcost = _landbos.deriv_insuranceMultiplierAndCost(
            self.farmSize, self.performanceBond)
        J = np.array([[0.0, 0.0], [dtcc, dfoundationcost]])

        return J


class Markup(Component):

    transportationCost = Float(iotype='in', units='USD', desc='transportation cost')
    contingency = Float(3.0, iotype='in', desc='%')
    warranty = Float(0.02, iotype='in', desc='%')
    useTax = Float(0.0, iotype='in', desc='%')
    overhead = Float(5.0, iotype='in', desc='%')
    profitMargin = Float(5.0, iotype='in', desc='%')

    alpha = Float(iotype='out', desc='multiplier portion of markup cost')
    cost = Float(iotype='out', units='USD', desc='constant portion of markup cost')

    def execute(self):
        values = _landbos.markupMultiplierAndCost(self.transportationCost,
            self.contingency, self.warranty, self.useTax, self.overhead,
            self.profitMargin)
        self.alpha = values['alpha']
        self.cost = values['cost']

    def list_deriv_vars(self):

        inputs = ('transportationCost',)
        outputs = ('alpha', 'cost',)

        return inputs, outputs

    def provideJ(self):

        dtransportationcost = _landbos.deriv_markupMultiplierAndCost(self.contingency,
            self.warranty, self.useTax, self.overhead, self.profitMargin)
        J = np.array([[0.0], [dtransportationcost]])

        return J


class Total(Component):

    turbine_cost = Float(iotype='in', units='USD')
    nTurbines = Int(iotype='in', desc='number of turbines')
    transportation_cost = Float(iotype='in', units='USD')
    engineering_cost = Float(iotype='in', units='USD')
    powerperf_cost = Float(iotype='in', units='USD')
    roads_cost = Float(iotype='in', units='USD')
    compound_cost = Float(iotype='in', units='USD')
    building_cost = Float(iotype='in', units='USD')
    foundation_cost = Float(iotype='in', units='USD')
    erection_cost = Float(iotype='in', units='USD')
    elecmat_cost = Float(iotype='in', units='USD')
    elecinst_cost = Float(iotype='in', units='USD')
    substation_cost = Float(iotype='in', units='USD')
    transmission_cost = Float(iotype='in', units='USD')
    projmgmt_cost = Float(iotype='in', units='USD')
    development_cost = Float(iotype='in', units='USD')
    insurance_cost = Float(iotype='in', units='USD')
    markup_cost = Float(iotype='in', units='USD')

    insurance_alpha = Float(iotype='in')
    markup_alpha = Float(iotype='in')

    multiplier = Float(1.0, iotype='in')

    cost = Float(iotype='out', units='USD', desc='total BOS cost')

    missing_deriv_policy = 'assume_zero'

    def execute(self):

        self.cost = self.transportation_cost + self.engineering_cost + \
            self.powerperf_cost + self.roads_cost + self.compound_cost + \
            self.building_cost + self.foundation_cost + self.erection_cost + \
            self.elecmat_cost + self.elecinst_cost + self.substation_cost + \
            self.transmission_cost + self.projmgmt_cost + self.development_cost + \
            self.insurance_cost + self.markup_cost

        alpha = self.insurance_alpha + self.markup_alpha

        # multiplier
        self.cost /= (1.0 - alpha)

        # remove TCC so only BOS is left
        TCC = self.turbine_cost * self.nTurbines
        self.cost -= TCC

        self.cost *= self.multiplier


    def list_deriv_vars(self):

        inputs = ('turbine_cost', 'transportation_cost', 'engineering_cost', 'powerperf_cost',
            'roads_cost', 'compound_cost', 'building_cost', 'foundation_cost', 'erection_cost',
            'elecmat_cost', 'elecinst_cost', 'substation_cost', 'transmission_cost',
            'projmgmt_cost', 'development_cost', 'insurance_cost', 'markup_cost', 'multiplier')
        outputs = ('cost',)


        return inputs, outputs

    def provideJ(self):

        alpha = self.insurance_alpha + self.markup_alpha
        dcost = self.multiplier / (1 - alpha) * np.ones(18)
        dcost[0] = -self.multiplier * self.nTurbines
        dcost[-1] = self.cost / self.multiplier

        J = np.array([dcost])

        return J


class NREL_Land_BOSSE(Assembly):

    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    rotor_diameter = Float(iotype='in', units='m', desc='rotor diameter')
    hub_height = Float(iotype='in', units='m', desc='hub height')
    turbine_number = Int(iotype='in', desc='number of turbines')
    voltage = Float(iotype='in', units='kV', desc='interconnect voltage')
    distInter = Float(iotype='in', units='mi', desc='distance to interconnect')
    terrain = Enum('FLAT_TO_ROLLING', ('FLAT_TO_ROLLING', 'RIDGE_TOP', 'MOUNTAINOUS'),
        iotype='in', desc='terrain options')
    layout = Enum('SIMPLE', ('SIMPLE', 'COMPLEX'), iotype='in',
        desc='layout options')
    soil = Enum('STANDARD', ('STANDARD', 'BOUYANT'), iotype='in',
        desc='soil options')

    turbine_cost = Float(iotype='in', units='USD')
    # TCC = Float(iotype='in', units='USD/kW', desc='turbine capital cost per kW')
    RNA_mass = Float(iotype='in', units='kg', desc='tower top mass')

    multiplier = Float(1.0, iotype='in')

    # If left at default of -1 then these values will be calculated
    # otherwise override with whatever you want
    constructionTime = Int(-1, iotype='in', units='mo', desc='construction time')
    buildingSize = Float(-1, iotype='in', units='ft**2', desc='O&M building size')
    tempMetTowers = Float(-1, iotype='in', desc='temporary meteorological towers')
    permanentMetTowers = Float(-1, iotype='in', desc='permananet meteorological towers')
    weatherDelayDays = Int(-1, iotype='in', units='d', desc='weather delay days')
    craneBreakdowns = Int(-1, iotype='in', desc='crane breakdowns')
    accessRoadEntrances = Int(-1, iotype='in', desc='access road entrances')

    # advanced inputs
    deliveryAssistRequired = Bool(False, iotype='in', desc='delivery assist required')
    padMountTransformer = Bool(True, iotype='in', desc='pad mount transformer required')
    newSwitchyardRequired = Bool(True, iotype='in', desc='new switchyard required')
    rockTrenchingLength = Float(10.0, iotype='in', desc='rock trenching required (% of collector cable length)')
    thermalBackfill = Float(0.0, iotype='in', units='mi', desc='MV thermal backfill')
    overheadCollector = Float(0.0, iotype='in', units='mi', desc='MV overhead collector')
    performanceBond = Bool(False, iotype='in', desc='performance bond')
    contingency = Float(3.0, iotype='in', desc='%')
    warranty = Float(0.02, iotype='in', desc='%')
    useTax = Float(0.0, iotype='in', desc='%')
    overhead = Float(5.0, iotype='in', desc='%')
    profitMargin = Float(5.0, iotype='in', desc='%')
    developmentFee = Float(5.0, iotype='in', desc='development fee (in millions of dollars)')
    transportDist = Float(0.0, iotype='in', units='mi', desc='transportation distance')

    bos_costs = Float(iotype='out', units='USD', desc='total BOS cost')

    def configure(self):

        self.add('fs', FarmSize())
        self.add('default', Defaults())
        self.add('transportation', Transportation())
        self.add('engineering', Engineering())
        self.add('powerperf', PowerPerformance())
        self.add('roads', AccessRoads())
        self.add('compound', SiteCompound())
        self.add('building', Building())
        self.add('foundation', Foundations())
        self.add('erection', Erection())
        self.add('elecmat', ElecMaterials())
        self.add('elecinst', ElecInstallation())
        self.add('substation', Substation())
        self.add('transmission', Transmission())
        self.add('projmgmt', ProjectMgmt())
        self.add('development', Development())
        self.add('insurance', Insurance())
        self.add('markup', Markup())
        self.add('total', Total())


        self.driver.workflow.add(['fs', 'default', 'transportation', 'engineering',
            'powerperf', 'roads', 'compound', 'building', 'foundation',
            'erection', 'elecmat', 'elecinst', 'substation', 'transmission',
            'projmgmt', 'development', 'insurance', 'markup', 'total'])

        # connections to fs
        self.connect('machine_rating', 'fs.rating')
        self.connect('turbine_number', 'fs.nTurbines')

        # connections to default
        self.connect('turbine_number', 'default.nTurbines')
        self.connect('fs.farmSize', 'default.farmSize')
        self.connect('constructionTime', 'default.override_constructionTime')
        self.connect('accessRoadEntrances', 'default.override_accessRoadEntrances')
        self.connect('weatherDelayDays', 'default.override_weatherDelayDays')
        self.connect('craneBreakdowns', 'default.override_craneBreakdowns')
        self.connect('buildingSize', 'default.override_buildingSize')
        self.connect('permanentMetTowers', 'default.override_permanentMetTowers')
        self.connect('tempMetTowers', 'default.override_tempMetTowers')

        # connections to transportation
        self.connect('turbine_cost/machine_rating', 'transportation.TCC')
        self.connect('machine_rating', 'transportation.rating')
        self.connect('turbine_number', 'transportation.nTurbines')
        self.connect('hub_height', 'transportation.hubHeight')
        self.connect('transportDist', 'transportation.transportDist')

        # connections to engineering
        self.connect('turbine_number', 'engineering.nTurbines')
        self.connect('fs.farmSize', 'engineering.farmSize')

        # connections to powerperf
        self.connect('hub_height', 'powerperf.hubHeight')
        self.connect('default.permanentMetTowers', 'powerperf.permanentMetTowers')
        self.connect('default.tempMetTowers', 'powerperf.tempMetTowers')

        # connections to roads
        self.connect('terrain', 'roads.terrain')
        self.connect('layout', 'roads.layout')
        self.connect('turbine_number', 'roads.nTurbines')
        self.connect('rotor_diameter', 'roads.diameter')
        self.connect('default.constructionTime', 'roads.constructionTime')
        self.connect('default.accessRoadEntrances', 'roads.accessRoadEntrances')

        # connections to compound
        self.connect('default.constructionTime', 'compound.constructionTime')
        self.connect('default.accessRoadEntrances', 'compound.accessRoadEntrances')
        self.connect('fs.farmSize', 'compound.farmSize')

        # connections to building
        self.connect('default.buildingSize', 'building.buildingSize')

        # connections to foundation
        self.connect('machine_rating', 'foundation.rating')
        self.connect('rotor_diameter', 'foundation.diameter')
        self.connect('RNA_mass', 'foundation.topMass')
        self.connect('hub_height', 'foundation.hubHeight')
        self.connect('soil', 'foundation.soil')
        self.connect('turbine_number', 'foundation.nTurbines')

        # connections to erection
        self.connect('machine_rating', 'erection.rating')
        self.connect('hub_height', 'erection.hubHeight')
        self.connect('turbine_number', 'erection.nTurbines')
        self.connect('default.weatherDelayDays', 'erection.weatherDelayDays')
        self.connect('default.craneBreakdowns', 'erection.craneBreakdowns')
        self.connect('deliveryAssistRequired', 'erection.deliveryAssistRequired')

        # connections to elecmat
        self.connect('terrain', 'elecmat.terrain')
        self.connect('layout', 'elecmat.layout')
        self.connect('fs.farmSize', 'elecmat.farmSize')
        self.connect('rotor_diameter', 'elecmat.diameter')
        self.connect('turbine_number', 'elecmat.nTurbines')
        self.connect('padMountTransformer', 'elecmat.padMountTransformer')
        self.connect('thermalBackfill', 'elecmat.thermalBackfill')

        # connections to elecinst
        self.connect('terrain', 'elecinst.terrain')
        self.connect('layout', 'elecinst.layout')
        self.connect('fs.farmSize', 'elecinst.farmSize')
        self.connect('rotor_diameter', 'elecinst.diameter')
        self.connect('turbine_number', 'elecinst.nTurbines')
        self.connect('rockTrenchingLength', 'elecinst.rockTrenchingLength')
        self.connect('overheadCollector', 'elecinst.overheadCollector')

        # connections to substation
        self.connect('voltage', 'substation.voltage')
        self.connect('fs.farmSize', 'substation.farmSize')

        # connections to transmission
        self.connect('voltage', 'transmission.voltage')
        self.connect('distInter', 'transmission.distInter')
        self.connect('newSwitchyardRequired', 'transmission.newSwitchyardRequired')

        # connections to projmgmt
        self.connect('default.constructionTime', 'projmgmt.constructionTime')

        # connections to development
        self.connect('developmentFee', 'development.developmentFee')

        # connections to insurance
        self.connect('turbine_cost/machine_rating', 'insurance.TCC')
        self.connect('fs.farmSize', 'insurance.farmSize')
        self.connect('foundation.cost', 'insurance.foundationCost')
        self.connect('performanceBond', 'insurance.performanceBond')

        # connections to markup
        self.connect('transportation.cost', 'markup.transportationCost')
        self.connect('contingency', 'markup.contingency')
        self.connect('warranty', 'markup.warranty')
        self.connect('useTax', 'markup.useTax')
        self.connect('overhead', 'markup.overhead')
        self.connect('profitMargin', 'markup.profitMargin')

        # connections to total
        self.connect('turbine_cost', 'total.turbine_cost')
        self.connect('turbine_number', 'total.nTurbines')
        self.connect('transportation.cost', 'total.transportation_cost')
        self.connect('engineering.cost', 'total.engineering_cost')
        self.connect('powerperf.cost', 'total.powerperf_cost')
        self.connect('roads.cost', 'total.roads_cost')
        self.connect('compound.cost', 'total.compound_cost')
        self.connect('building.cost', 'total.building_cost')
        self.connect('foundation.cost', 'total.foundation_cost')
        self.connect('erection.cost', 'total.erection_cost')
        self.connect('elecmat.cost', 'total.elecmat_cost')
        self.connect('elecinst.cost', 'total.elecinst_cost')
        self.connect('substation.cost', 'total.substation_cost')
        self.connect('transmission.cost', 'total.transmission_cost')
        self.connect('projmgmt.cost', 'total.projmgmt_cost')
        self.connect('development.cost', 'total.development_cost')
        self.connect('insurance.cost', 'total.insurance_cost')
        self.connect('markup.cost', 'total.markup_cost')
        self.connect('insurance.alpha', 'total.insurance_alpha')
        self.connect('markup.alpha', 'total.markup_alpha')
        self.connect('multiplier', 'total.multiplier')

        # connections to outputs
        self.connect('total.cost', 'bos_costs')




if __name__ == '__main__':

    bos = NREL_Land_BOSSE()
    bos.machine_rating = 2000
    bos.rotor_diameter = 110
    bos.hub_height = 100
    bos.turbine_number = 100
    bos.voltage = 137
    bos.distInter = 5
    bos.terrain = 'FLAT_TO_ROLLING'
    bos.layout = 'COMPLEX'
    bos.soil = 'STANDARD'
    bos.turbine_cost = 1000.0 * bos.machine_rating
    bos.RNA_mass = 88.0 *1000

    bos.run()

    print bos.bos_costs


    c0 = bos.transportation.cost
    delta = 1e-6*bos.turbine_cost
    bos.turbine_cost += delta
    bos.run()
    print (bos.transportation.cost - c0)/delta

    bos.check_gradient(inputs=['rotor_diameter', 'hub_height', 'RNA_mass', 'turbine_cost'], outputs=['total.cost'])
    # bos.check_gradient(inputs=['turbine_cost'], outputs=['transportation.cost'])
    # bos.check_gradient(inputs=['rotor_diameter', 'hub_height', 'RNA_mass', ('transportation.TCC', 'insurance.TCC')], outputs=['total.cost'])




