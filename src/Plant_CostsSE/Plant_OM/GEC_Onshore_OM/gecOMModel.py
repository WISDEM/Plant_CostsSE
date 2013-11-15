# gecOMModel.py
# 2012 04 24

''' Implementation of GEC O&M Model in python
    G. Scott, NREL, May 2012
    
    class OMPlant: a wind plant and its O&M values
    main(): create an OMPlant
            read system input file (systems, components, failure rates)
            compute failure rates and costs for each component
            (print rates and costs for a specified year)
            print final tables of total costs per year
'''

# Note:
#   Some small tweaks have been made to the code to make it (almost) agree
#   with the GEC O&M spreadsheet:
#   - rndwbl has been added (and set to True) to round Weibull distributions
#     to one decimal place
#   - a small (0.0000001) adj factor has been added to CummFailYr in gecOMComp.py
#     to help with errors from internal representation (e.g., adding 0.6 to
#     itself 10 times is actually 5.9999...., which is less than 6.0)
#     This seems to work well. 2012 05 17

import sys, os, csv
import re
import time
from math import *
from socket import gethostname
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

import gecFailure as fail
import gecOMComp as gcmp

#-------------------------------------------------------------------------------

class OMPlant(object):
    ''' an object representing a wind plant and its O&M-related parameters '''
    
    def __init__(self,name,nyrs=20,sysdict=None):
        self.names = name
        self.nyrs = nyrs
        
        # defaults
        
        self.turbPwr = 1500 # pwr per turbine in kW
        self.nTurb   = 60
        self.capFact = 0.44 # capacity factor (between 0.0 and 1.0)
        self.tConsume = 2.348 # k$/yr
        
        self.burden     =  0.35
        self.srTechWage = 18.00
        self.jrTechWage = 12.00       
        
        self.partsRepl   = [0] * self.nyrs
        self.salLabor    = [0.0] * self.nyrs
        self.wageLabor   = [0.0] * self.nyrs
        self.siteMaint   = [14.0] * self.nyrs
        self.equipment   = [24.0] * self.nyrs

        # 0 - Site Manager Salary
        # 1 - Admin. Asst. Salary
        # 2 - Sr. Tech Wage
        # 3 - Jr. Tech Wage
        
        self.smSalary = 85000
        self.aaSalary = 35000
        self.mult   = [1, 1, 2080, 2080]  # convert hrs to yrs for wages
        self.nstaff = [ [0 for x in range(self.nyrs)] for x in range(4) ] # number of staff
        self.stfCst = [ [0 for x in range(self.nyrs)] for x in range(4) ] # staff costs by job type and year
        
        self.nstaff = [ ([1 for x in range(20)]),
                        ([2 for x in range(20)]),
                        ([2 for x in range(10)] + [3 for x in range(10)] ),
                        ([4 for x in range( 5)] + [6 for x in range(10)] + [8 for x in range(5)] ) ]

        if (sysdict is not None): # parse dictionary argument
            if ('turbPwr' in sysdict):
                self.turbPwr = sysdict['turbPwr']
            if ('nTurb' in sysdict):
                self.nTurb = sysdict['nTurb']
            if ('capFact' in sysdict):
                self.capFact = sysdict['capFact']
            if ('tConsume' in sysdict):
                self.tConsume = sysdict['tConsume']
            if ('burden' in sysdict):
                self.burden = sysdict['burden']
            if ('srTechWage' in sysdict):
                self.srTechWage = sysdict['srTechWage']
            if ('jrTechWage' in sysdict):
                self.jrTechWage = sysdict['jrTechWage']
            if ('smSalary' in sysdict):
                self.smSalary = sysdict['smSalary']
            if ('aaSalary' in sysdict):
                self.aaSalary = sysdict['aaSalary']
            if ('siteMaint' in sysdict):
                self.siteMaint = [sysdict['siteMaint']] * self.nyrs
            if ('equipment' in sysdict):
                self.equipment = [sysdict['equipment']] * self.nyrs
            #nstaff?
            
        self.projPwr = self.nTurb * self.turbPwr
        self.laborRate  = (2.0*self.jrTechWage + 1.0*self.srTechWage) / 3.0 * 0.001
        self.swrate = [self.smSalary, self.aaSalary, self.srTechWage, self.jrTechWage]
        self.consumables = [self.nTurb*self.tConsume] * self.nyrs

        for i in range(4):
            for j in range(20):
                self.stfCst[i][j] = self.nstaff[i][j] * (self.mult[i] * (1.0+self.burden) * self.swrate[i])
                #print "{:d} {:2d} Cst {:8.1f}".format(i,j,self.stfCst[i][j])
            #print self.stfCst[i]
        

        #for j in range(20):
        #    print "stfCST {:2d} {:6.2f} {:6.2f} {:6.2f} {:6.2f} ".format(j, 
        #      self.stfCst[0][j]*0.001, 
        #      self.stfCst[1][j]*0.001, 
        #      self.stfCst[2][j]*0.001, 
        #      self.stfCst[3][j]*0.001)        

        for j in range(20):
            self.salLabor[j]  = (self.stfCst[0][j] + self.stfCst[1][j]) * 0.001
            self.wageLabor[j] = (self.stfCst[2][j] + self.stfCst[3][j]) * 0.001
            #print "SAL {:6.2f} = {:6.2f} + {:6.2f} ".format(self.salLabor[j],  self.stfCst[0][j]*0.001, self.stfCst[1][j]*0.001),
            #print "  WAG {:6.2f} = {:6.2f} + {:6.2f} ".format(self.wageLabor[j], self.stfCst[2][j]*0.001, self.stfCst[3][j]*0.001)
        #print self.salLabor
        #print self.wageLabor
            
        pass
        
    def tblcomp(self,x,itbl):
        y = x
        if (itbl > 0):
            y = [yy * 1000 / self.nTurb for yy in y]
        if (itbl == 2):
            y = [yy / self.turbPwr for yy in y]
        if (itbl == 3):
            y = [yy / (self.turbPwr* 8760 * self.capFact) for yy in y]
        return y

    def yprint(self,v,fmt,scale=1.0):
        for i in range(self.nyrs):
            #print "{:5.2f} ".format(v[i]),
            print "{0:{1}}\t".format(v[i]*scale,fmt),
        print

    def compTotals(self,itbl,*v):
        t = [0] * self.nyrs
        #print "CompTotals has {} args".format(len(v))
        for iarg in range(len(v)):
            #print "  L({}) = {}".format(iarg,len(v[iarg]))
            vv = self.tblcomp(v[iarg], itbl)
            for j in range(len(vv)):
                t[j] += vv[j]
        return t
        
    def resultsTable(self,itbl):
        """ This function prints the results tables 
            itbl is 0,1,2 or 3
        """
        rttitles = ['Total Project $000/year',
                    '$/Turbine/year',
                    '$/kW/year',
                    '\xA2/kW-hr']
        #            '$/kW-hr']
        fmts = ["4.0f", "5.0f", ".2f", ".4f"]
        scl = [ 1.0, 1.0, 1.0, 100.0]
                    
        print rttitles[itbl]
        print "Year\t",
        for yr in range(1,self.nyrs+1):
            print "{0:}\t".format(yr),
        print
    
        totals = self.compTotals(itbl,self.partsRepl,  
                                      self.consumables,
                                      self.salLabor,
                                      self.wageLabor,
                                      self.siteMaint,
                                      self.equipment
                                      )
        
        print "{}\t".format('Parts Replacement'),; self.yprint(self.tblcomp(self.partsRepl,  itbl), fmts[itbl], scale=scl[itbl])
        print "{}\t".format('Consumables      '),; self.yprint(self.tblcomp(self.consumables,itbl), fmts[itbl], scale=scl[itbl])
        print "{}\t".format('Salaried Labor   '),; self.yprint(self.tblcomp(self.salLabor,itbl),    fmts[itbl], scale=scl[itbl])
        print "{}\t".format('Wage-based Labor '),; self.yprint(self.tblcomp(self.wageLabor,itbl),   fmts[itbl], scale=scl[itbl])
        print "{}\t".format('Site Maintenance '),; self.yprint(self.tblcomp(self.siteMaint,itbl),   fmts[itbl], scale=scl[itbl])
        print "{}\t".format('Equipment        '),; self.yprint(self.tblcomp(self.equipment,itbl),   fmts[itbl], scale=scl[itbl])
        print "{}\t".format('Total            '),; self.yprint(totals,                              fmts[itbl], scale=scl[itbl])
        print
        print
        
        
    def barchart(self,itbl):
        ''' draw a barchart of various component costs by year '''
                 
        rttitles = ['Total Project $000/year',
                    '$/Turbine/year',
                    '$/kW/year',
                    '\xA2/kW-hr']
        barlabels = ['Parts Replacement',
                     'Consumables      ',
                     'Salaried Labor   ',
                     'Wage-based Labor ',
                     'Site Maintenance ',
                     'Equipment        ',
                     'Total            ']

        totals = self.compTotals(itbl,self.partsRepl,  
                                      self.consumables,
                                      self.salLabor,
                                      self.wageLabor,
                                      self.siteMaint,
                                      self.equipment
                                      )

        N = 20
        ind = np.arange(N)  # the x locations for the groups
        width = 0.10       # the width of the bars
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        yval = [None] * N
        yval[0] = self.tblcomp(self.partsRepl,  itbl)
        yval[1] = self.tblcomp(self.consumables,itbl)
        yval[2] = self.tblcomp(self.salLabor,itbl)  
        yval[3] = self.tblcomp(self.wageLabor,itbl) 
        yval[4] = self.tblcomp(self.siteMaint,itbl) 
        yval[5] = self.tblcomp(self.equipment,itbl)
        yval[6] = self.tblcomp(totals,itbl)
         
        rects = [None] * N
        lgndrct = [None] * N
        barclrs = ( '#9999FF', '#993366', '#FFFFCC', '#CCFFFF', '#660066', '#FF8080', '#00FF00')
        for i in range(7):
            rects[i] = ax.bar(ind+i*width, yval[i], width, color=barclrs[i])
            lgndrct[i] = rects[i][0]
        
        # add some
        ax.set_ylabel(rttitles[itbl])
        ax.set_title('Project Age (yrs)')
        ax.set_xticks(ind+width)
        
        xlbls = [None] * N
        for i in range(1,21):
            xlbls[i-1] = "{}".format(i)
        ax.set_xticklabels( ('G1', 'G2', 'G3', 'G4') )
        ax.set_xticklabels( xlbls )
        
        #ax.legend( (rects[0][0], rects[1][0]), (barlabels), loc='upper left' )
        ax.legend( (lgndrct), (barlabels), loc='upper left' )
        
        def autolabel(rects):
            # attach some text labels
            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                        ha='center', va='bottom')
        
        autolabel(rects[0])
        autolabel(rects[6])
        
        plt.show()
        
#------------------------------------------------

def rdflt(arg):
    """ Read contents of string argument and convert to float (or None) """
    if (len(arg) < 1):
        return None
    return float(arg)
    
#------------------------------------------------

def readSysFile(fname,sysDict, nTurb, laborRate, rndwbl=False, debug=False):
    """ This function reads the system file to describe the systems and components 
        Adds system keys to sysDict
        Adds components (OMComponent) to sysDict[systems]
        Adds crane costs to individual components
    """

    nyrs = 20
    try:
        f = open(fname)
    except:
        sys.stdout.write ("Error opening or reading %s\n" % fname)
        return 0
    else:
        if (debug):
            sys.stdout.write ("readSysFile opened %s\n" % fname)

    reader = csv.reader(f)
    for row in reader:
        if not row: # ignore blank lines
            continue
        if (len(row[0]) < 1):
            continue
        if (row[0] == 'System'):
            continue
        if (row[0].startswith('#')):  # comments
            continue
        #print "Len(row) = {}".format(len(row))

        # Crane Costs
        
        if (row[0].startswith('CRANE')):
            cSys,cComp,cCost = row[1:4]
            cSys  = cSys.strip()
            cComp = cComp.strip()
            if not cSys in sysDict:
                sys.stderr.write("Key {} not found in sysDict\n".format(cSys))
                continue
            if not cComp in sysDict[cSys]:
                sys.stderr.write("Key {} not found in sysDict[{}]\n".format(cComp,cSys))
                continue
            sysDict[cSys][cComp].craneCost = float(cCost) * 0.001
            sysDict[cSys][cComp].updateVals()
            if (debug):
                print "Set CraneCost to {} for {} {}".format(sysDict[cSys][cComp].craneCost, cSys, cComp)
            continue    

        # Component parameters
        
        # 0    1         2        3        4     5     6     7        8    9     10
        System,Component,FailPred,FailRate,WeibA,WeibB,Mlife,NperTurb,Cost,Labor,Crane = row[0:11]
        WeibA    = rdflt(row[4])
        WeibB    = rdflt(row[5])
        FailRate = rdflt(row[3])
        NperTurb = int(row[7])
        if Crane in ['TRUE', 'True', 'true', 't']:
            Crane = True
        elif Crane in ['FALSE', 'False', 'false', 'f']:
            Crane = False
        Cost = float(Cost)
        if (Cost < 0):
            Cost = 0.0
                
        if (not(System in sysDict)):
            if (debug):
                print "Adding {0} to SysDict".format(System) 
            sysDict[System] = {}
        if (not(row[1] in sysDict[System])):
            if (debug):
                print "Adding {0} to SysDict({1})".format(Component,System) 
            sysDict[System][Component] = gcmp.OMComponent(Component,WeibB,WeibA,nyrs,
                                                          NperTurb * nTurb,
                                                          failRate=FailRate,
                                                          fp=FailPred,
                                                          laborHours=float(Labor),
                                                          laborRate=laborRate,
                                                          partCost=Cost,
                                                          crane=Crane,  # need craneCost
                                                          rndwbl=rndwbl)
    print 
    f.close()
    
    return 
    
#--------------------- MAIN ------------------

def main():
    print ("Running %s at %s on %s" % (sys.argv[0], time.asctime(), gethostname()) )

    omp = OMPlant("gecOM Test Plant")
    nTurb = omp.nTurb
    
    # Read component description file
    
    if (len(sys.argv) == 1):
        print ("\nUSAGE: {0} file\n".format(sys.argv[0]))
        sys.exit()

    # sysDict is a dictionary of dictionaries
    #   First key is system (e.g., 'Rotor')
    #     Second key is component (e.g., 'Pitch gear')
    #   Contents of sysDict['Rotor']['Pitch gear'] is
    #     an OMComponent object
            
    sysDict = {}
    rndwbl = False
    rndwbl = True
    readSysFile(sys.argv[1], sysDict, nTurb, omp.laborRate*(1.0+omp.burden), rndwbl=rndwbl)
    
    # Print system/component tree
    
    prntyr = 9
    print "Costs for year {}".format(prntyr+1)
    for system in sysDict:
        print "{}".format(system)
        for comp in sysDict[system]:
            sysDict[system][comp].compute()
            print "    {:30}".format(sysDict[system][comp].name),
            
            for iyr in range(omp.nyrs):
                omp.partsRepl[iyr] += sysDict[system][comp].compCostYr[iyr]
                if (iyr == prntyr):
                    print "    {:7.2f} ({:2.0f}*{:7.2f}) {:7.2f}".format(
                       sysDict[system][comp].compCostYr[iyr],
                       sysDict[system][comp].incrFailYr[iyr], 
                       sysDict[system][comp].totalCostEvent, 
                       omp.partsRepl[iyr])
    print
    
    for itbl in range(4):
        omp.resultsTable(itbl)
    
    omp.barchart(0)
        
    # Access specific component
    #print sysDict['Rotor']['Pitch gear']
    #sysDict['Rotor']['Pitch gear'].dump()
    sysDict['Rotor']['Pitch motor'].dump()        
    
   # Green Cumm Failures per year table should be Incremental Failures per year
    
    #cumFailPerYr =
    #cost = 
    #compCostPerYr(i) = sum(cost(i))
    
    #partsRepl = compCostPerYr(i) # 'Failure&Cost Distribution'!CW169  # Parts Replacement varies by year   
    #consum    = nTurb*totConsumables / 1000 # Consumables      
    #salLabor  = (mgrSalary+aaSalary) / 1000 # Salaried Labor      varies by year
    #wageLabor = (srtWage+jrtWage)    / 1000 # Wage-based Labor    varies by year
    #siteMaint = totMaint             / 1000 # Site Maintenance 
    #equip     = totEquip             / 1000 # Equipment        


if __name__ == "__main__":

    main()
