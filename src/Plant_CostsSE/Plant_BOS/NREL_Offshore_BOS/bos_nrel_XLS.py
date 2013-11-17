"""
bos_nrel_XLS.py
Implements the NREL BOS Excel spreadsheet as a win32com object
 
Imported by bos_nrel_Component.py and bos_nrel_Assembly.py for use with openMDAO

Created by George Scott on 2012-08-01.
Modified by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

################
### preliminary mac notes for excel.
# seems like they want us to use applescript to actually drive excel (plenty of other options for just manipulating data in sheets,
# but wee need  to actually run VB scripts in excel)
# To run AS from cmd line: osascript <apple script file>
# So a plausible path is for our code to write AS, then run it as a system call.
######

##############


import sys, os

from Plant_CostsSE.xcel_wrapper import ExcelWrapper

# shnums - sheet names and corresponding numbers in NREL BOS spreadsheet
#   Most inputs will be on sheet 'Input' (1)
#   Most outputs are read from sheet 'Results' (2)

shnums = {     
    'Input'           :  2, 
    'Results'         :  3, 
 }

#-------------------------------------------------------------------------
    
class bos_nrel_XLS(object):
    '''
    class bos_nrel_XLS:
      a Python interface to the NREL BOS Excel spreadsheet
      
      Note: for setCell() and getCell(), the user MUST know the exact
        cell row and column indicies in 'Input' and 'Results'
        respectively. Results are unpredictable otherwise.
    '''

    #-----------------------
        
    def __init__(self,debug=False):
        self.debug = debug
        self.xcel = ExcelWrapper()
        if (self.debug):
            sys.stdout.write ("Created bos_nrel_XLS object\n")
            
    #-----------------------
        
    def ssopen(self,ssfile=None):
        """
        open the NREL BOS spreadsheet
        """
        
        if (ssfile is not None):
            if (not os.path.isfile(ssfile)):
                print "xlsfile not found: {}".format(ssfile)
                raise ValueError('No such file: {}'.format(ssfile))
                return -1
            self.xlsfile = ssfile

        if (not os.path.isfile(self.xlsfile)):
            print "xlsfile not valid: {}".format(self.xlsfile)
            raise ValueError('No such file: {}'.format(self.xlsfile))
            return -1
            
        # Start Excel
        res = self.xcel.openWorkbook(self.xlsfile)
        if res != 0:
            return res

#        if (self.debug):    
#            print "Found %d sheets" % self.ss.Sheets.Count
#            for i in range(1,self.ss.Sheets.Count+1):
#                print "%2d %s" % (i, self.ss.Worksheets(i).Name)
#            print
            
        return 0
        
    #-----------------------
        
    def ssclose(self):
        """
        close the NREL BOS spreadsheet
        """

        # Close spreadsheet without saving
        self.xcel.closeWorkbook()
        
        # If user doesn't have any other workbooks open in Excel, quit Excel
        if self.xcel.countWorkbooks() == 0:
            self.xcel.closeExcel()
    
    #-----------------------
        
    def setCell(self,irow,icol,value):
        """
        set an input cell in the NREL BOS spreadsheet, 'Input' worksheet
        """
#        self.ss.Activate()
#        self.xl.Worksheets("Input").Activate()
#        sh = self.ss.ActiveSheet
#        sh.Cells(irow,icol).Value = value
#        sh.Calculate()

        res = self.xcel.setCell(irow, icol, value, "Input")
    
    #-----------------------
        
    def getCell(self,irow,icol):
        """
        get an output cell in the NREL BOS spreadsheet, 'Results' worksheet
        """
#        cval = self.ss.Worksheets(shnums['Results']).Cells(irow,icol).Value
        cval = self.xcel.getCell(irow, icol, "Results")
        return float(cval)
    
    #-----------------------
        
    def getInputCell(self,irow,icol):
        """
        get an input cell in the NREL BOS spreadsheet, 'Input' worksheet
        """
#        return self.ss.Worksheets(shnums['Input']).Cells(irow,icol).Value
        cval = self.xcel.getCell(irow, icol, "Input")
        return cval
    #-----------------------
        
    def getCost(self):
        """
        return the value of cents/kWH from the NREL BOS spreadsheet, 'Results' worksheet
        """

#        return float(self.ss.Worksheets(shnums['Results']).Cells(3,2).Value)
        return getCell(3,2,"Results")
    
    #-----------------------
        
    def printCosts(self):
        """
        print calculated costs from the NREL BOS spreadsheet
        returns revenue loss, repair costs and totals
        """
        
        iTotalCost     =  3  
        iFoundation    = 10
        iEngineering   =  7  
        iPermitting    =  8  
        iPortsStaging  =  9  
        iElectrical    = 11 
        iVessels       = 12 
        iAddlCapExpend = 13 
            
#        if (PlatformIsWindows()):
        if (False):
            self.ss.Activate()        
            self.xl.Worksheets("Results").Activate()
            sh = self.ss.ActiveSheet

            TotalCost     = float(sh.Cells(iTotalCost    ,2).Value)
            Foundation    = float(sh.Cells(iFoundation    ,2).Value)
            Engineering   = float(sh.Cells(iEngineering  ,2).Value)
            Permitting    = float(sh.Cells(iPermitting   ,2).Value)
            PortsStaging  = float(sh.Cells(iPortsStaging ,2).Value)
            Electrical    = float(sh.Cells(iElectrical   ,2).Value)
            Vessels       = float(sh.Cells(iVessels      ,2).Value)
            AddlCapExpend = float(sh.Cells(iAddlCapExpend,2).Value)
        else:
            TotalCost     = float(self.xcel.getCell(iTotalCost    ,2,"Results"))
            Foundation    = float(self.xcel.getCell(iFoundation   ,2,"Results"))
            Engineering   = float(self.xcel.getCell(iEngineering  ,2, "Results"))
            Permitting    = float(self.xcel.getCell(iPermitting   ,2, "Results"))
            PortsStaging  = float(self.xcel.getCell(iPortsStaging ,2, "Results"))
            Electrical    = float(self.xcel.getCell(iElectrical   ,2, "Results"))
            Vessels       = float(self.xcel.getCell(iVessels      ,2, "Results"))
            AddlCapExpend = float(self.xcel.getCell(iAddlCapExpend,2, "Results"))

        print "TotalCost     ${:15,.1f}".format(TotalCost     * 1e6) 
        print "Foundation    ${:15,.1f}".format(Foundation    * 1e3) 
        print "Engineering   ${:15,.1f}".format(Engineering   * 1e3)  
        print "Permitting    ${:15,.1f}".format(Permitting    * 1e3)  
        print "PortsStaging  ${:15,.1f}".format(PortsStaging  * 1e3)  
        print "Electrical    ${:15,.1f}".format(Electrical    * 1e3) 
        print "Vessels       ${:15,.1f}".format(Vessels       * 1e3) 
        print "AddlCapExpend ${:15,.1f}".format(AddlCapExpend * 1e3) 
        
    #-----------------------
        
    def execute(self):
        """
        EXAMPLES: ways to access the NREL BOS spreadsheet
        """
        
        #c61 = currency
        #i61 = cost 
              
        isht = shnums['Results']
        print "Cost %.3f %s" % ( self.ss.Worksheets(isht).Cells(61,9).Value, 
                                 self.ss.Worksheets(isht).Cells(61,3).Text)   

        # Modify the input data sheet

        self.ss.Activate()        
        self.xl.Worksheets("Input").Activate()
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
            self.ss.Worksheets(shnums['Input']).Cells(5,15).Value = salary
            self.ss.Worksheets(shnums['Input']).Calculate()
            print "Salary {:.1f} Cost {:.1f}".format(salary,self.ss.Worksheets(shnums['Results']).Cells(61,9).Value)
        self.ss.Worksheets(shnums['Input']).Cells(5,15).Value = 150000
        self.ss.Worksheets(shnums['Input']).Calculate()

#--------------------------------------------------------------------------------------------

def example(ssfile=None):

    if (ssfile is not None):
		    bos = bos_nrel_XLS(debug=True)
		
		    import time
		    tt = time.time()
		
		    istat = bos.ssopen(ssfile)  #TODO: this flag currently gets set to 0 though program still works...
		    
		    bos.printCosts()
		    
		    bos.setCell(7,2,50) # change number of turbines
		    
		    bos.printCosts()
		    print
		     
		    print "Cost/kWH {:5.3f}".format(bos.getCell(3,2)) # get cost
		    
		    bos.ssclose()
		
		    print
		    
		    print "Elapsed time: {:.3f} seconds".format(time.time()-tt) 

if __name__ == "__main__":

    ssfile  = 'C:/Python27/openmdao-0.3.0/twister/models/BOS/Offshore BOS model-Optimized IOM 12-11-29.xlsx'
    example(ssfile)