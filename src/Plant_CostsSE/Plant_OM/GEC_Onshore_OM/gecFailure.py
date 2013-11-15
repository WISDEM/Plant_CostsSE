# gecFailure.py
# 2012 04 23
 # Duplicate the functions of the failure rate tables in
 #  'O&M Cost Estimator_RevA_22Jun06 Linked.xls'
 
from math import *
import matplotlib.pyplot as plt

#------------------------------------------------------------

class FailTable(object):
        
    def __init__(self, wk=2.0, wc=10.0, nyrs=20, partsAffected=0, rndwbl=False):
        '''
        class FailTable
          a failure table for a given Weibull failure rate
          
          table: a 'nyrs-1' rows (generations) by 'nyrs' columns table
          total: nyrs values of table totals by year (over all generations)
          partsAffected: 'nyrs-1' values (generations)
        
          NOTE: most arrays are 0-indexed
        
          set rndwbl to True to emulate rounding in GEC Excel spreadsheet
        '''
        
        self.wk = wk
        self.wc = wc
        self.nyrs = nyrs
        self.parts = partsAffected
        self.partsAffected = [0] * (self.nyrs-1)
        self.failPerGen    = [0] * (self.nyrs-1)
        self.total = [0] * (self.nyrs)
        self.table = [ [ None for i in range(nyrs) ] for j in range(nyrs-1) ]         
        self.rndwbl = rndwbl
        
        for jgen in range(self.nyrs-1):
            if (jgen == 0):
                self.partsAffected[jgen] = partsAffected
            else:
                self.partsAffected[jgen] = self.total[jgen-1]
                
            for iyr in range(self.nyrs):
                if (jgen > iyr):
                    continue
                if (jgen == 0):
                    self.table[jgen][iyr] = self.parts * weibull(iyr+1,self.wk,self.wc)
                else:
                    self.table[jgen][iyr] = self.partsAffected[jgen] * weibull(iyr+1-jgen,self.wk,self.wc)
                    
                if (self.rndwbl): # emulate rounding in GEC spreadsheet
                    self.table[jgen][iyr] = round(self.table[jgen][iyr],1)
                    
                self.total[iyr]       += self.table[jgen][iyr]
                self.failPerGen[jgen] += self.table[jgen][iyr]

 
    def printFail(self):
        print "{:7.4f}\n".format(float(self.total[0]))
        #print "{:s}\n".format(self.total)
        pass
                
    def printTable(self):
        print "Failure Table"
        for jgen in range(self.nyrs-1):
            print "{:6.2f} ".format(self.partsAffected[jgen])
            print "G{:02d}   ".format(jgen+1),
            for iyr in range(self.nyrs):
                if (self.table[jgen][iyr] is not None):
                    print "{:5.2f} ".format(self.table[jgen][iyr]),
                else:
                    print "      ",
            print "| {:6.2f} ".format(self.failPerGen[jgen])
            print "\n"
            
        print "Total ",
        for iyr in range(self.nyrs):
            if (self.total[iyr] is not None):
                print "{:5.2f} ".format(self.total[iyr]),
            else:
                print "      ",
        print "\n"
                
    def plotFail(self, ttl=""):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(range(1,self.nyrs+1), self.total, 'o-')
        #plt.plot(range(1,self.nyrs+1), self.total, 'o-')
        plt.xlabel('Years')
        plt.ylabel('Failure Rate')
        ttl = " ".join([ttl," Part Failure History"])
        plt.title(ttl)
        ax.grid(True)
        plt.show()
        pass

    def tblColAvg(self, iyr):
        sum = 0
        cnt = 0
        for jgen in range(self.nyrs-1):
            if (self.table[jgen][iyr] is not None):
                sum += self.table[jgen][iyr]
                cnt += 1
        if (cnt > 0):
            sum = sum / cnt
        return sum

#-------------------------------------------------------------------------------

def weibull(X,K,L):
    ''' return Weibull probability at speed X for distribution with k=K, c=L '''
    w = (K/L) * ((X/L)**(K-1)) * exp(-((X/L)**K))
    return w

#------------------------------------------------------------

def main():
    nyrs = 20
    wk = 2.0
    wc = 10.0
    partsAffected = 180
    parts = 180
    meanLife = wc * log(2.0)**(1.0/wk)
    total = [0] * (nyrs+2)

    ftbl = FailTable(wk=wk, wc=wc, nyrs=nyrs, partsAffected=parts )    
    ftbl.printTable()
    ftbl.plotFail(ttl="FailTable Test")
    
#-------------------------------------------------------------------------------

if __name__ == "__main__":
	main()

