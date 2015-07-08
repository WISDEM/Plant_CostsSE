#!/usr/bin/env python
# encoding: utf-8
"""
test_gradients.py

Created by Andrew Ning on 2014-05-12.
Copyright (c) NREL. All rights reserved.
"""

import unittest

from landbos import Transportation, PowerPerformance, AccessRoads, Foundations, \
    Erection, ElecMaterials, ElecInstallation, Insurance, Markup, Total
from commonse.utilities import check_gradient_unit_test, check_for_missing_unit_tests


# -----------------------------------------------------------
# These tests only apply to LandBOSsmooth.c (not LandBOS.c)
# -----------------------------------------------------------


class TestTransportation(unittest.TestCase):

    def test1(self):

        t = Transportation()
        t.TCC = 1000.0
        t.rating = 5000.0
        t.nTurbines = 100
        t.hubHeight = 90.0
        t.transportDist = 3.0

        check_gradient_unit_test(self, t)


class TestPowerPerformance(unittest.TestCase):

    def test1(self):

        pp = PowerPerformance()
        pp.hubHeight = 100.0
        pp.permanentMetTowers = 3.0
        pp.tempMetTowers = 2.0

        check_gradient_unit_test(self, pp)


    def test2(self):

        pp = PowerPerformance()
        pp.hubHeight = 90.0
        pp.permanentMetTowers = 3.0
        pp.tempMetTowers = 2.0

        check_gradient_unit_test(self, pp)


    def test3(self):

        pp = PowerPerformance()
        pp.hubHeight = 80.0
        pp.permanentMetTowers = 3.0
        pp.tempMetTowers = 2.0

        check_gradient_unit_test(self, pp)


class TestAccessRoads(unittest.TestCase):

    def test1(self):

        ar = AccessRoads()
        ar.terrain = 'FLAT_TO_ROLLING'
        ar.layout = 'SIMPLE'
        ar.nTurbines = 100
        ar.diameter = 120.0
        ar.constructionTime = 1
        ar.accessRoadEntrances = 2

        check_gradient_unit_test(self, ar)


class TestFoundations(unittest.TestCase):

    def test1(self):

        found = Foundations()
        found.rating = 5000.0
        found.diameter = 120.0
        found.topMass = 88.0 * 1000
        found.hubHeight = 100.0
        found.soil = 'STANDARD'
        found.nTurbines = 100

        check_gradient_unit_test(self, found)


class TestErection(unittest.TestCase):

    def test1(self):

        erec = Erection()
        erec.rating = 5000.0
        erec.hubHeight = 100.0
        erec.nTurbines = 100
        erec.weatherDelayDays = 4
        erec.craneBreakdowns = 3
        erec.deliveryAssistRequired = True


        check_gradient_unit_test(self, erec)


class TestElecMaterials(unittest.TestCase):

    def test1(self):

        em = ElecMaterials()
        em.terrain = 'FLAT_TO_ROLLING'
        em.layout = 'SIMPLE'
        em.farmSize = 500.0
        em.diameter = 120.0
        em.nTurbines = 100
        em.padMountTransformer = True
        em.thermalBackfill = 10.0


        check_gradient_unit_test(self, em)


class TestElecInstallation(unittest.TestCase):

    def test1(self):

        comp = ElecInstallation()
        comp.terrain = 'FLAT_TO_ROLLING'
        comp.layout = 'SIMPLE'
        comp.farmSize = 500.0
        comp.diameter = 120.0
        comp.nTurbines = 100
        comp.rockTrenchingLength = 12.0
        comp.overheadCollector = 10.0

        check_gradient_unit_test(self, comp)


class TestInsurance(unittest.TestCase):

    def test1(self):

        comp = Insurance()
        comp.TCC = 1000.0
        comp.farmSize = 500.0
        comp.foundationCost = 1e7
        comp.performanceBond = True

        check_gradient_unit_test(self, comp)


class TestMarkup(unittest.TestCase):

    def test1(self):

        comp = Markup()
        comp.transportationCost = 200000000.0
        comp.contingency = 3.0
        comp.warranty = 0.02
        comp.useTax = 0.0
        comp.overhead = 5.0
        comp.profitMargin = 5.0

        check_gradient_unit_test(self, comp)


class TestTotal(unittest.TestCase):

    def test1(self):

        comp = Total()
        comp.turbine_cost = 2000000.0
        comp.nTurbines = 100
        comp.transportation_cost = 200000000.0
        comp.engineering_cost = 1112596.36154
        comp.powerperf_cost = 912133.333333
        comp.roads_cost = 7713048.0
        comp.compound_cost = 901575.0
        comp.building_cost = 633735.251317
        comp.foundation_cost = 11286436.7811
        comp.erection_cost = 9382605.40137
        comp.elecmat_cost = 14675585.0
        comp.elecinst_cost = 7830230.0
        comp.substation_cost = 5530851.41472
        comp.transmission_cost = 4246267.80099
        comp.projmgmt_cost = 2607139.155
        comp.development_cost = 5000000.0
        comp.insurance_cost = 665728.735622
        comp.markup_cost = -26040000.0
        comp.insurance_alpha = 0.0056
        comp.markup_alpha = 0.1302
        comp.multiplier = 1.3

        check_gradient_unit_test(self, comp)




if __name__ == '__main__':

    import landbos
    check_for_missing_unit_tests([landbos])
    unittest.main()


