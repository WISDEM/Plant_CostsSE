"""
ecnomXLS.py
Implements the ECN O&M Excel spreadsheet as a win32com object
 
Imported by ecnom.py and ecnAssy.py for use with openMDAO

Created by George Scott on 2012-08-01.
Modified by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

import sys, os
from twister.components.global_config import PlatformIsWindows
from twister.models.xcel_wrapper import ExcelWrapper

#import win32com.client as win32

# shnums - sheet names and corresponding numbers in ECN O&M spreadsheet
#   Most inputs will be on sheet 'General' (5)
#   Most outputs are read from sheet 'OverviewResults' (12)

shnums = {     
    'Data'            :  1, 
    'Definition'      :  2, 
    'Fitting'         :  3, 
    'WorkDays'        :  4, 
    'General'         :  5, 
    'FaultTypesWT'    :  6, 
    'FaultTypesBOP'   :  7, 
    'Equipment'       :  8, 
    'FixedCosts'      :  9, 
    'LowIntervals'    : 10, 
    'DataSeason'      : 11, 
    'OverviewResults' : 12, 
    'Costs_yr'        : 13, 
    'Costs_win'       : 14, 
    'Costs_spr'       : 15, 
    'Costs_sum'       : 16, 
    'Costs_aut'       : 17, 
    'Costs_yr_graphs' : 18, 
    'Application'     : 19 
 }

# Failure frequencies are found in sheet 'FaultTypesWT'
 
wt_failfreq_col = 2
wt_failfreq_row = {
    'MDA10' :  19, # Rotor system - blades
    'MDA20' :  27, # Rotor system - Hub
    'MDC'   :  35, # Blade adjustment
    'MDK10' :  43, # Drive train - main shaft/bearing
    'MDK30' :  51, # Drive train - brake system
    'MDL'   :  59, # Yaw gearbox
    'MDX'   :  67, # Hydraulic system
    'MDY'   :  75, # Control and protection system turbine
    'MKA'   :  83, # Generator 
    'MKY'   :  91, # Control and protection system generator
    'MSA'   :  99, # Generator lead / transmission cables
    'MST'   : 107, # Transformer
    'MUD'   : 115, # Machinery enclosure
    'UMD'   : 123, # Turbine structure / tower
    'XA'    : 131, # Heating, ventilation, air conditioning
    'XM'    : 139, # Crane system
    'AB'    : 147, # Lightning protection / grounding
    'MD'    : 155, # Remote Resets
    }

#euro = u"\u20AC"

#-------------------------------------------------------------------------
    
class ecnomXLS(object):
    '''
    class ecnomXLS:
      a Python interface to the ECN O&M Excel spreadsheet
      
      Note: for setCell() and getCell(), the user MUST know the exact
        cell row and column indicies in 'General' and 'OverviewResults'
        respectively. Results are unpredictable otherwise.
        
      methods execute(), failsweep() and salsweep() are provide only as
      examples.
         
    '''
    #-----------------------
        
    def __init__(self,debug=False):
        self.debug = debug
        self.xcel = ExcelWrapper()
        
        # row indices into 'General' worksheet    
        self.i_price = 5
        self.i_nturb = 6
        self.i_lftim = 7
        
        if (self.debug):
            sys.stdout.write ("Created ecnomXLS object\n")
            
    #-----------------------
        
    def ssopen(self,ssfile=None):
        """
        open the ECN O&M spreadsheet
        """

        if (ssfile is not None):
            if (not os.path.isfile(ssfile)):
                print "xlsfile not found: {}".format(ssfile)
                raise ValueError('No such file: {}'.format(ssfile))
                #return 0
            self.xlsfile = ssfile

        if (not os.path.isfile(self.xlsfile)):
            print "xlsfile not valid: {}".format(self.xlsfile)
            raise ValueError('No such file: {}'.format(self.xlsfile))

        # Start Excel
        res = self.xcel.openWorkbook(self.xlsfile)
        if res != 0:
            return res
        
#        if (self.debug):    
#            print "Found %d sheets" % self.ss.Sheets.Count
#            for i in range(1,self.ss.Sheets.Count+1):
#                print "%2d %s" % (i, self.ss.Worksheets(i).Name)
#            print
        
    #-----------------------
        
    def ssclose(self):
        """
        close the ECN O&M spreadsheet
        """

        # Close spreadsheet without saving
        self.xcel.closeWorkbook()       
#        self.ss.Close(False)
        
        # If user doesn't have any other workbooks open in Excel, quit Excel
        if self.xcel.countWorkbooks() == 0:
            self.xcel.closeExcel() 
    
    #-----------------------
        
    def setCell(self,irow,icol,value):
        """
        set an input cell in the ECN O&M spreadsheet, 'General' worksheet
        """
        res = self.xcel.setCell(irow, icol, value, "General")

#        self.ss.Activate()
#        self.xl.Worksheets("General").Activate()
#        sh = self.ss.ActiveSheet
#        sh.Cells(irow,icol).Value = value
#        sh.Calculate()
    
    #-----------------------
        
    def getCell(self,irow,icol):
        """
        get an output cell in the ECN O&M spreadsheet, 'OverviewResults' worksheet
        """

        #self.xl.Worksheets("OverviewResults").Activate()
        #sh = self.ss.ActiveSheet
        #value = sh.Cells(irow,icol).Value
        
        # if value.__class__ is 'unicode' or 'NoneType',
        #   we have an error
       
        #return (value)
#        return (self.ss.Worksheets(shnums['OverviewResults']).Cells(irow,icol).Value)
        cval = self.xcel.getCell(irow, icol, "OverviewResults")
        return cval
    #-----------------------
        
    def getInputCell(self,irow,icol):
        """
        get an input cell in the ECN O&M spreadsheet, 'Input' worksheet
        """
#        return self.ss.Worksheets(shnums['General']).Cells(irow,icol).Value
        cval = self.xcel.getCell(irow, icol, "General")
        return cval
    
    #-----------------------    
        
    def getCost(self):
        """
        return the value of cents/kWH from the ECN O&M spreadsheet, 'OverviewResults' worksheet
        """

#        return (self.ss.Worksheets(shnums['OverviewResults']).Cells(3,6).Value)
        cval = self.xcel.getCell(irow, icol, "OverviewResults")
        return cval
    
    #-----------------------
        
    def printCosts(self):
        """
        print calculated costs from the ECN O&M spreadsheet
        returns revenue loss, repair costs and totals
        """

#        self.ss.Activate()        
#        self.xl.Worksheets("OverviewResults").Activate()
#        sh = self.ss.ActiveSheet
        iRowRL = 24 # revenue losses
        iRowRC = 56 # repair costs
        
        rl = []
        rc = []
        ttl = []
        head = ['Winter', 'Spring', 'Summer', 'Fall', 'Year', 'Total']
        
        print ' ' * 12,
        for h in head:
            if h != None:
              print "{0:>6} ".format(h),
        print 
        
        print '{0:12}'.format('Revenue Loss'),
        for i in range(4,10):
            val = self.xcel.getCell(iRowRL,i,"OverviewResults")
#            val = sh.Cells(iRowRL,i).Value
            rl.append(val)
            print "{0:6.0f} ".format(val),
        print
        
        print '{0:12}'.format("Repair Cost"),
        for i in range(4,10):
            val = self.xcel.getCell(iRowRC,i,"OverviewResults")
#            val = sh.Cells(iRowRC,i).Value
            rc.append(val)
            print "{0:6.0f} ".format(val),
        print
        
        print '{0:12}'.format("Total"),
        for i in range(4,10):
            val = self.xcel.getCell(iRowRL,i,"OverviewResults") + self.xcel.getCell(iRowRC,i,"OverviewResults")
#            val = sh.Cells(iRowRL,i).Value+sh.Cells(iRowRC,i).Value
            ttl.append(val)
            print "{0:6.0f} ".format(val),
        print

        return (rl, rc, ttl)
        
    #-----------------------
    #-----------------------
        
    def execute(self):
        """
        EXAMPLES: ways to access the ECN O&M spreadsheet
        """
        
        #c61 = currency
        #i61 = cost 
              
        isht = shnums['OverviewResults']
        print "Cost %.3f %s" % ( self.ss.Worksheets(isht).Cells(61,9).Value, 
                                 self.ss.Worksheets(isht).Cells(61,3).Text)   

        # Modify the input data sheet
        
        self.xl.Worksheets("General").Activate()
        sh = self.ss.ActiveSheet
        inpCol = 3
      
        # Set x and y in spreadsheet, calculate and return f(x,y)

        price = 0.15 # Euros/kWh
        nturb = 100
        lftim = 18
        
        sh.Cells(self.i_price,    inpCol).Value = price
        sh.Cells(self.i_nturb,    inpCol).Value = nturb
        sh.Cells(self.i_lftim,    inpCol).Value = lftim
        
        sh.Calculate()
        
        self.printCosts()
    
    #-----------------------
        
    def salsweep(self):
        """
        EXAMPLE: Sweep over a salary range
        """
        
        for i in range(8):
            salary = 150000 + i*10000.
            self.ss.Worksheets(shnums['General']).Cells(5,15).Value = salary
            self.ss.Worksheets(shnums['General']).Calculate()
            print "Salary {:.1f} Cost {:.1f}".format(salary,self.ss.Worksheets(shnums['OverviewResults']).Cells(61,9).Value)
        self.ss.Worksheets(shnums['General']).Cells(5,15).Value = 150000
        self.ss.Worksheets(shnums['General']).Calculate()

    #-----------------------
        
    def failsweep(self):
        """
        EXAMPLE: Sweep over a failure rate range
        """
        
        isht = shnums['FaultTypesWT']
        fail_rate = self.ss.Worksheets(isht).Cells(wt_failfreq_row['MDK10'],wt_failfreq_col).Value
        fr_mult = 1.3
        
        for i in range(5):
            self.ss.Worksheets(isht).Cells(wt_failfreq_row['MDK10'],wt_failfreq_col).Value = fail_rate
            self.ss.Worksheets(isht).Calculate()
            print "FailRate {:.2f} Cost {:.1f}".format(fail_rate,self.ss.Worksheets(shnums['OverviewResults']).Cells(61,9).Value)
            fail_rate *= fr_mult



#--------------------------------------------------------------------------------------------

def example():

    om = ecnomXLS()

    import time
    tt = time.time()

    ssfile  = r'C:/Python27/openmdao-0.3.0/twister/models/OM/ECN/ECN O&M Tool IO&M Baseline.xls' #TODO - machine dependency
    
    om.ssopen(ssfile=ssfile)
    
    print "Cost with 50 turbines"
    (rl,rc,ttl) = om.printCosts() 
    print "Cost/kWH {:5.3f}".format(om.getCell(3,6)) # get cost/kWH
    
    om.setCell(6,3,100) # change number of turbines

    print "\nCost with 100 turbines"    
    (rl,rc,ttl) = om.printCosts() 
    print "Cost/kWH {:5.3f}".format(om.getCell(3,6)) # get cost/kWH

    om.setCell(6,3,50) # change number of turbines
    
    om.ssclose()
    
    print "Elapsed time: {:.3f} seconds".format(time.time()-tt)

if __name__ == "__main__":

    example()
