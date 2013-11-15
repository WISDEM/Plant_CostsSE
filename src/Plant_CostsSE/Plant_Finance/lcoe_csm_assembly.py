"""
LCOE_csm_ssembly.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys, os, fileinput

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from twister.components.global_config import WESEConfig, get_dict

from twister.components.varTrees import Turbine, PlantBOS, PlantOM

# NREL cost and scaling model components for BOS, O&M, TCC and Finance
from twister.components.tcc_csm_component import tcc_csm_component
from twister.components.bos_csm_component import bos_csm_component
from twister.components.om_csm_component  import om_csm_component
from twister.components.fin_csm_component import fin_csm_component
# NREL cost and scaling model AEP assembly
from twister.assemblies.aep_csm_assembly import aep_csm_assembly

from twister.models.csm.csmDriveEfficiency import DrivetrainEfficiencyModel, csmDriveEfficiency

class lcoe_csm_assembly(Assembly):

    # ---- Design Variables ----------
    # See passthrough variables below
    # system input variables
    # turbine
    ratedPower = Float(5000.0, units = 'kW', iotype='in', desc= 'rated machine power in kW')
    rotorDiameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine')
    maxTipSpeed = Float(80.0, units = 'm/s', iotype='in', desc= 'maximum allowable tip speed for the rotor')
    drivetrainDesign = Int(1, iotype='in', desc= 'drivetrain design type 1 = 3-stage geared, 2 = single-stage geared, 3 = multi-generator, 4 = direct drive')
    hubHeight = Float(90.0, units = 'm', iotype='in', desc='hub height of wind turbine above ground / sea level')
    # plant
    seaDepth = Float(20.0, units = 'm', iotype='in', desc = 'sea depth for offshore wind project')
    altitude = Float(0.0, units = 'm', iotype='in', desc= 'altitude of wind plant')
    turbineNumber = Int(100, iotype='in', desc = 'total number of wind turbines at the plant')
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')    

    # ------------- Outputs -------------- 
    # See passthrough variables below

    def __init__(self,inputs=None):
        """ Creates a new LCOE Assembly object """

        super(lcoe_csm_assembly, self).__init__()
        
        # Assign inputs from user
        self.AssignInputs(inputs)

                
    def configure(self):
        ''' configures assembly by adding components, creating the workflow, and connecting the component i/o within the workflow '''

        # Create assembly instances (mode swapping ocurrs here)
        self.SelectComponents()

        # Set up the workflow
        self.WorkflowAdd()

        # Connect the components
        self.WorkflowConnect()
    
    def execute(self):

        print "In {0}.execute()...".format(self.__class__)

        super(lcoe_csm_assembly, self).execute()  # will actually run the workflow

        return self.lcoe  #TODO - output variable(s) should depend on user preference
        
    
    #------- Supporting methods --------------

    def SelectComponents(self):
        '''
        Component selections for wrapping different models which calculate main outputs for cost analysis
        '''

        aepa = aep_csm_assembly()
        self.add('aep1', aepa)

        tccc = tcc_csm_component()
        self.add('tcc', tccc)

        bosc = bos_csm_component()
        self.add('bos', bosc)

        omc = om_csm_component()
        self.add('om',  omc)

        finc = fin_csm_component()
        self.add('fin', finc)

    def WorkflowAdd(self):
        ''' modifies workflow to add the appropriate components '''

        self.driver.workflow.add(['aep1', 'tcc', 'bos', 'om', 'fin'])  

    def WorkflowConnect(self):
        ''' creates variable connections based on mode combinations - i/o between components depending on which models are selected '''

        # create passthroughs for key input variables of interest
        # turbine
        self.create_passthrough('tcc.bladeNumber')
        self.create_passthrough('tcc.advancedBlade')
        self.create_passthrough('tcc.thrustCoefficient')
        self.create_passthrough('aep1.maxPowerCoefficient')
        self.create_passthrough('aep1.optTipSpeedRatio')
        self.create_passthrough('aep1.cutInWindSpeed')
        self.create_passthrough('aep1.cutOutWindSpeed')
        self.create_passthrough('tcc.crane')
        self.create_passthrough('tcc.advancedBedplate')
        # plant
        self.create_passthrough('aep1.shearExponent')
        self.create_passthrough('aep1.windSpeed50m')
        self.create_passthrough('aep1.weibullK')
        self.create_passthrough('aep1.airDensity')
        self.create_passthrough('aep1.soilingLosses')
        self.create_passthrough('aep1.arrayLosses')
        self.create_passthrough('aep1.availability')
        self.create_passthrough('fin.fixedChargeRate')
        self.create_passthrough('fin.constructionTime')
        self.create_passthrough('fin.projectLifetime')

        # connect i/o to component and assembly inputs
        # turbine configuration
        # rotor
        self.connect('rotorDiameter', ['aep1.rotorDiameter', 'tcc.rotorDiameter', 'bos.rotorDiameter'])
        self.connect('maxTipSpeed', ['aep1.maxTipSpeed', 'tcc.maxTipSpeed'])
        self.connect('aep1.ratedWindSpeed', 'tcc.ratedWindSpeed')
        self.connect('aep1.maxEfficiency', 'tcc.maxEfficiency')
        # drivetrain
        self.connect('ratedPower', ['aep1.ratedPower', 'tcc.ratedPower', 'bos.ratedPower', 'om.ratedPower', 'fin.ratedPower'])
        self.connect('drivetrainDesign', ['aep1.drivetrainDesign', 'tcc.drivetrainDesign'])
        # tower
        self.connect('hubHeight', ['aep1.hubHeight', 'tcc.hubHeight', 'bos.hubHeight'])   
        # plant configuration
        # climate
        self.connect('altitude', ['aep1.altitude', 'tcc.altitude'])
        self.connect('seaDepth', ['tcc.seaDepth', 'bos.seaDepth', 'om.seaDepth', 'fin.seaDepth'])
        # plant operation       
        self.connect('turbineNumber', ['aep1.turbineNumber', 'bos.turbineNumber', 'om.turbineNumber', 'fin.turbineNumber']) 
        # financial
        self.connect('year', ['tcc.year', 'bos.year', 'om.year'])
        self.connect('month', ['tcc.month', 'bos.month', 'om.month'])
        self.connect('tcc.turbineCost', ['bos.turbineCost', 'fin.turbineCost'])
        self.connect('aep1.aep', ['om.aep', 'fin.aep'])
        self.connect('bos.BOScost', 'fin.BOScost')
        self.connect('om.plantOM.preventativeMaintenanceCost', 'fin.preventativeMaintenanceCost')
        self.connect('om.plantOM.correctiveMaintenanceCost', 'fin.correctiveMaintenanceCost')
        self.connect('om.plantOM.landLeaseCost', 'fin.landLeaseCost')
 
        # create passthroughs for key output variables of interest
        # aep
        self.create_passthrough('aep1.ratedRotorSpeed')
        self.create_passthrough('aep1.ratedWindSpeed')
        self.create_passthrough('aep1.powerCurve')
        self.create_passthrough('aep1.aep')
        self.create_passthrough('aep1.aepPerTurbine')
        self.create_passthrough('aep1.capacityFactor')
        # tcc
        self.create_passthrough('tcc.turbineCost')
        self.create_passthrough('tcc.turbineMass')
        self.create_passthrough('tcc.turbine')
        # bos
        self.create_passthrough('bos.BOScost')
        self.create_passthrough('bos.plantBOS')
        # om
        self.create_passthrough('om.OnMcost')
        self.create_passthrough('om.plantOM')
        # fin
        self.create_passthrough('fin.lcoe')
        self.create_passthrough('fin.coe')

    def AssignInputs(self,inputs=None):

        if inputs != None:
            for key in inputs:
                self.inputs[key] = inputs[key]
        
            # assign inputs to variables for assembly
            for key in self.inputs:
                # Turbine configuration
                # rotor
                if key == 'rotorDiameter':
                    self.rotorDiam = float(self.inputs[key])
                if key == 'maxTipSpeed':
                    self.maxTipSpeed = float(self.inputs[key])
                if key == 'bladeNumber':
                    self.bladeNumber = int(self.inputs[key])
                if key == 'advancedBlade':
                    if int(self.inputs[key]) == 0:
                       self.advancedBlade = False
                    else:
                       self.advancedBlade = True
                if key == 'maxPowerCoefficient':
                    self.maxPowerCoefficient = float(self.inputs[key])
                if key == 'optTipSpeedRatio':
                    self.optTipSpeedRatio = float(self.inputs[key])
                if key == 'cutInWindSpeed':
                    self.cutInWindSpeed = float(self.inputs[key])
                if key == 'cutOutWindSpeed':
                    self.cutOutWindSpeed = float(self.inputs[key])
                if key == 'thrustCoefficient':
                    self.thrustCoefficient = float(self.inputs[key])
                # drivetrain
                if key == 'ratedPower':
                    self.ratedPower = float(self.inputs[key])
                if key == 'drivetrainDesign':
                    self.drivetrainDesign = int(self.inputs[key])
                if key == 'crane':
                    if int(self.inputs[key]) == 0:
                      self.crane = False
                    else:
                      self.crane = True
                if key == 'advancedBedplate':
                    self.advancedBedplate = int(self.inputs[key])
                # tower
                if key == 'hubHeight':
                    self.hubHeight = float(self.inputs[key])
                    
                # Plant configuration
                if key == 'windSpeed50m':
                    self.windSpeed50m = float(self.inputs[key])
                if key == 'weibullK':
                    self.weibullK = float(self.inputs[key])
                if key == 'shearExponent':
                    self.shearExponent = float(self.inputs[key])
                if key == 'seaDepth':
                    self.seaDepth = float(self.inputs[key])
                if key == 'altitude':
                    self.altitude = float(self.inputs[key])
                if key == 'airDensity':
                    self.airDensity = float(self.inputs[key])
                if key == 'year':
                    self.year = int(self.inputs[key])
                if key == 'month':
                    self.month = int(self.inputs[key])
                if key == 'turbineNumber':
                    self.turbineNumber = int(self.inputs[key])
                if key == 'soilingLosses':
                    self.soilingLosses = float(self.inputs[key])
                if key == 'arrayLosses':
                    self.arrayLosses = float(self.inputs[key])
                if key == 'availability':
                    self.availability = float(self.inputs[key])
                if key == 'discountRate':
                    self.discountRate = float(self.inputs[key])
                if key == 'taxRate':
                    self.taxRate = float(self.inputs[key])
                if key == 'discountRate':
                    self.discountRate = float(self.inputs[key])
                if key == 'constructionTime':
                    self.constructionTime = float(self.inputs[key])
                if key == 'projectLifetime':
                    self.projectLifetime = float(self.inputs[key])

if __name__=="__main__":

    lcoe = lcoe_csm_assembly()
    
    lcoe.advancedBlade = True
    lcoe.aep1.drive.drivetrain = csmDriveEfficiency(1)
    #lcoe.rotorDiameter *= 0.9
    #lcoe.ratedPower *= 0.9
    
    lcoe.execute()
    
    print "LCOE: {0}".format(lcoe.lcoe)
    print "COE: {0}".format(lcoe.coe)
    print "\n"
    print "AEP per turbine: {0}".format(lcoe.aep / lcoe.turbineNumber)
    print "Turbine Cost: {0}".format(lcoe.turbineCost)
    print "BOS costs per turbine: {0}".format(lcoe.BOScost / lcoe.turbineNumber)
    print "OnM costs per turbine: {0}".format(lcoe.OnMcost / lcoe.turbineNumber)
    print
    print "Turbine output variable tree:"
    lcoe.turbine.printVT()
    print
    print "Plant BOS output variable tree:"
    lcoe.plantBOS.printVT()
    print
    print "Plant OM output variable tree:"
    lcoe.plantOM.printVT()

    fname = 'CSM.txt'
    f = file(fname,'w')

    f.write("File Name: | {0}\n".format(fname))
    f.write("Turbine Conditions:\n")
    f.write("Rated Power: | {0}\n".format(lcoe.ratedPower))
    f.write("Rotor Diameter: | {0}\n".format(lcoe.rotorDiameter))
    f.write("Rotor maximum tip speed: | {0}\n".format(lcoe.maxTipSpeed))
    f.write("Cost and mass outputs:\n")
    f.write("LCOE: |{0}\n".format(lcoe.lcoe))
    f.write("COE: |{0}\n".format(lcoe.coe))
    f.write("AEP : |{0}\n".format(lcoe.aep))
    f.write("Turbine Cost: |{0}\n".format(lcoe.turbineCost))
    f.write("BOS costs : |{0}\n".format(lcoe.BOScost))
    f.write("OnM costs : |{0}\n".format(lcoe.OnMcost))
    f.write("Turbine output variable tree:\n")
    lcoe.turbine.fwriteVT(f)
    f.write("Plant BOS output variable tree:\n")
    lcoe.plantBOS.fwriteVT(f)
    f.write("Plant OM output variable tree:\n")
    lcoe.plantOM.fwriteVT(f)
    f.write("AEP Statistics:\n")
    f.write("Capacity factor: |{0}\n".format(lcoe.capacityFactor))
    f.write("Rotor Power Curve and sound output:\n")
    for i in range(len(lcoe.powerCurve[0])):
      f.write("{0} | {1} \n".format(lcoe.powerCurve[0][i],lcoe.powerCurve[1][i]))
    f.close()