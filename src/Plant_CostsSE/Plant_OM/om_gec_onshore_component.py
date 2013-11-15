# gecOMComp.py
# 2012 05 08
# class for turbine or plant component as used in GEC O&M Model

#------------------------------------------------------------

from math import *

import gecFailure as fail

class OMComponent(object):
    """ OMComponent - a wind turbine or plant component with associated O&M costs, lifetimes and failure rates """
    def __init__(self,name,wk,wc,nyrs,parts, laborHours=10, laborRate=35, 
                                             crane=False, craneCost=60,
                                             partCost=350,
                                             fp=None,failRate=None,
                                             rndwbl=False):
        self.name     = name
        self.wk       = wk
        self.wc       = wc
        self.nyrs     = nyrs
        self.parts    = parts    # total parts per project
        self.failRate = failRate
        self.failPred = fp       # string starting with 'Weib' or 'Const'
        self.rndwbl   = rndwbl
        
        self.craneCost = 0.0
        self.crane = crane
        if (self.crane):
            self.craneCost = craneCost
            
        self.laborCost = laborRate * laborHours #* 0.001
        self.partCost  = partCost  * 0.001
        self.totalCostEvent = self.laborCost + self.craneCost + self.partCost
        
        self.nFailNYrs = 0
        
        self.CummFailYr = [0.0] * self.nyrs
        self.incrFailYr = [0]   * self.nyrs
        self.compCostYr = [0.0] * self.nyrs
        self.projFailYr = [0.0] * self.nyrs
        
        if (self.failPred is None): 
            print "No failure rate specified for {}".format(self.name)
        
        elif (self.failPred.startswith("Weib")):
            if (self.wc is None or self.wk is None):
                print "Missing Weibull parameters for {} - set to 0 failures".format(self.name)
                self.failPred = "ConstantRate"
                self.failRate = 0.0
            else:
                self.meanLife = self.wc * log(2.0)**(1.0/self.wk)
                self.ftbl = fail.FailTable(wk=self.wk, wc=self.wc, nyrs=self.nyrs, 
                    partsAffected=parts, rndwbl=self.rndwbl )
        
        elif (self.failPred.startswith("Const")):
            self.failRate = self.parts * failRate / (self.nyrs*100) # failures/project/yr
        
        else:
            print "Unknown failure mode '{}' specified for {}".format(self.failPred,self.name)
            
        
    def __str__(self):
        """ special attribute returns a string when string is needed """
        return "OMComponent: {0}".format (self.name)  
        
    def updateVals(self):
        """ recompute values after changes """
        self.totalCostEvent = self.laborCost + self.partCost
        if (self.crane):
            self.totalCostEvent += self.craneCost
        
    def compute(self):
        """ compute yearly values """
        cummFail = 0.0
        for iyr in range(self.nyrs):

            if (self.failPred.startswith("Const")):
                self.projFailYr[iyr] = self.failRate
            else:
                self.projFailYr[iyr] = self.ftbl.total[iyr]

            cummFail += self.projFailYr[iyr]
            #if (self.failPred.startswith("Const")):
            #    cummFail += 0.0000001  # emulate rounding in GEC Excel spreadsheet

            self.CummFailYr[iyr] = cummFail 
                
            if (iyr == 0):
                self.incrFailYr[iyr] = int(self.CummFailYr[iyr])
            else:
                #self.incrFailYr[iyr] = int(self.CummFailYr[iyr])-int(self.CummFailYr[iyr-1])
                adj = 0.0000001 # adjust for floating pt precision errors
                self.incrFailYr[iyr] = int(self.CummFailYr[iyr]+adj)-int(self.CummFailYr[iyr-1]+adj)
            self.nFailNYrs += self.incrFailYr[iyr]
            
            self.compCostYr[iyr] = self.incrFailYr[iyr] * self.totalCostEvent
        
    def dump(self):
        """ print yearly values """
        print self.name
        print "YR   CummF  PFail  IncrF  CCost"
        for iyr in range(self.nyrs):
            print "{0:2d} ".format(iyr+1),
            print "{0:6.2f} ".format(self.CummFailYr[iyr]),
            print "{0:5.2f} ".format(self.projFailYr[iyr]),
            print "{0:5d} ".format(self.incrFailYr[iyr]),
            print "{0:5.2f} ".format(self.compCostYr[iyr])
        print "Events/{}yrs/Project: {:4d}".format(self.nyrs,self.nFailNYrs)

#------------------------------------------------------------

def example():

    """ test OMComponent class by creating single instance, computing it and dumping it """
    nyrs = 20
    wk = 2.0
    wc = 10.0
    parts = 180
    
    brkcal = OMComponent("BrakeCalipers", wk, wc, nyrs, parts)
    #brkcal.ftbl.printFail()
    brkcal.ftbl.plotFail(ttl="BrakeCalipers")
    brkcal.ftbl.printTable()
    brkcal.compute()
    brkcal.dump()

if __name__ == "__main__":

    example()