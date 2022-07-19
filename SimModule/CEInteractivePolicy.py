import pandas as pd
import numpy as np


##### No Policy means that nominal interest rate is always 0
##### real interest rate then = -inflation, reflecting how savings are losing money in inflation
##### this should return an inflation spiral
##### we're gonna start with inflation = 0 (piT = 0 in the code, ik it's a bit confusing)
##### also, no CBbeta because central bank doesn't exist, so inflation = output gap for all periods

###Helper Methods

# def FindOptimumY(expectedinflation, ye=100, piT=2, alpha=1, beta=1):
#     ###optimum y found using intersect of next period's PC, MR
#     #this is central bank finding its target in response to this period's distance from equilibrium
#     y = (((alpha * beta) * (piT - expectedinflation)) / (1 + ((alpha ** 2) * (beta)))) + ye
#     return y

# def FindResponse(optimumY, A, a=0.75):
#     ###optimum r using optimum y
#     #this is cb finding real interest rate response to target to get to optimal y, using its IS curve
#     r = (A - optimumY) / a 
#     return r

def InflationfromY(y, ye=100, alpha=1, beta=1, piE=0):
    ###find inflation in economy from bargaining gap 
    pi = ((ye - y) / (alpha * beta)) + piE
    return pi

###Simulator

class CEInteractivesim():
    def __init__(self, ratelist, ye=100, rstar=4, alpha=1, beta=1, a=2, 
                piT=2, credibility=0):

        self.ratelist = ratelist        
        self.periods = len(ratelist)

        self.ye = ye
        self.rstar = rstar
        self.alpha = alpha
        self.beta = beta
        self.a = a
        self.piT = piT
        self.credibility = credibility
        self.anticredibility = 1 - credibility

        self.A = ye + (a * self.rstar)
        self.cols = ['Periods', 'Output Gap', 'GDP', 'Inflation', 'Expected Inflation', 'Lending real i.r.', 'Lending nom i.r.', 
                    'A']
        
    def DemandShock(self, size, temporary=True):
        self.size = size
        self.multiplier = (0.01 * self.size) + 1
        self.newA = self.A * self.multiplier ## not sure about this
        df = pd.DataFrame(columns=self.cols)

        period = 1
        while period < 5:
            periodseries = pd.Series(dtype=np.float64)
            periodseries['Periods'] = period
            periodseries['Output Gap'] = 0.0
            periodseries['GDP'] = self.ye
            periodseries['Inflation'] = self.piT
            periodseries['Expected Inflation'] = self.piT ####up to p5, piE = piT
            cbresponsei = self.ratelist[period-1]
            periodseries['Lending nom i.r.'] = cbresponsei
            periodseries['Lending real i.r.'] = cbresponsei - self.piT
            periodseries['A'] = self.A

            df.loc[period] = periodseries
            period += 1
        
        while period < 6: #period 5 only
            #periodseries = pd.Series(dtype=np.float64)
            periodseries['Periods'] = period
            #temporary demand shock
            periodseries['GDP'] = self.ye * self.multiplier
            periodseries['Output Gap'] = self.size
            inflation = self.piT + self.size
            periodseries['Inflation'] = inflation
            periodseries['Expected Inflation'] = self.piT ###In period 5, piE = pi(t-1) = piT (for all credibility)
            #cb response, finds PC where inflation = equilibrium output (this is next period's PC)
            #then find that pc intersect with MR and that output is optimal bargaining gap
            #it uses next period's PC, so the expected inflation it uses is this period's inflation for adaptive
            #this will be useless for non-adaptive expectations - needs rewrite
            cbresponsei = self.ratelist[period-1]
            periodseries['Lending nom i.r.'] = cbresponsei 
            periodseries['Lending real i.r.'] = cbresponsei - inflation
            periodseries['A'] = self.newA

            df.loc[period] = periodseries
            period += 1

        while period <= self.periods: #all post shock periods
            if temporary:
                periodseries['A'] = self.A
            else:
                periodseries['A'] = self.newA
            periodseries['Periods'] = period
            #beginning of recovery
            output = periodseries['A'] - (self.a * (cbresponsei - inflation))
            periodseries['GDP'] = output
            periodseries['Output Gap'] = output - self.ye
            periodseries['Expected Inflation'] = (self.credibility * self.piT) + (self.anticredibility * inflation)
            inflation = InflationfromY(output, alpha=self.alpha, beta=self.beta, piE=periodseries['Expected Inflation'])
            periodseries['Inflation'] = inflation
            #cb response: finds PC where expected inflation = equilibrium output
            #then find that pc intersect with MR and that output is optimal bargaining gap
            #gets optimal bargaining gap with r found with RX curve
            #again, expected inflation used for next period is this period's inflation for adaptive or anchored at piT
            cbresponsei = self.ratelist[period-1]
            periodseries['Lending nom i.r.'] = cbresponsei 
            periodseries['Lending real i.r.'] = cbresponsei - inflation
            #newq = FindQ(cbresponser)

            df.loc[period] = periodseries
            period += 1

        return df.round(4)

    def SupplyShock(self, size, temporary=True):
        self.size = size
        self.multiplier = (0.01 * self.size) + 1
        self.newye = self.ye * self.multiplier

        df = pd.DataFrame(columns=self.cols)

        period = 1
        while period < 5:
            periodseries = pd.Series(dtype=np.float64)
            periodseries['Periods'] = period
            periodseries['Output Gap'] = 0.0
            periodseries['GDP'] = self.ye
            periodseries['Inflation'] = self.piT
            periodseries['Expected Inflation'] = self.piT ####up to p5, piE = piT
            cbresponsei = self.ratelist[period-1]
            periodseries['Lending nom i.r.'] = cbresponsei
            periodseries['Lending real i.r.'] = cbresponsei - self.piT
            periodseries['A'] = self.A

            df.loc[period] = periodseries
            period += 1
        
        while period < 6:
            #periodseries = pd.Series(dtype=np.float64)
            periodseries['Periods'] = period
            #permanent supply shock changes ye, not y
            periodseries['GDP'] = self.ye
            outputgap = ((self.ye - self.newye) / self.ye) * 100
            periodseries['Output Gap'] = outputgap
            periodseries['Expected Inflation'] = self.piT 
            inflation = self.piT + outputgap
            periodseries['Inflation'] = inflation
            #cb response, finds PC where inflation = equilibrium output
            #then find that pc intersect with MR and that output is optimal bargaining gap
            #piE = df.loc[period - 1]['Inflation']
            cbresponsei = self.ratelist[period-1]
            periodseries['Lending nom i.r.'] = cbresponsei 
            periodseries['Lending real i.r.'] = cbresponsei - inflation
            periodseries['A'] = self.A

            df.loc[period] = periodseries
            period += 1

        while period <= self.periods:
            periodseries['Periods'] = period
            #beginning of recovery
            output = periodseries['A'] - (self.a * (cbresponsei - inflation))
            periodseries['GDP'] = output
            periodseries['Output Gap'] = output - (self.ye if temporary else self.newye)
            periodseries['Expected Inflation'] = (self.credibility * self.piT) + (self.anticredibility * inflation)
            if temporary:
                inflation = InflationfromY(output, alpha=self.alpha, beta=self.beta, piT=self.piT)
            else:
                inflation = InflationfromY(output, ye=self.newye, alpha=self.alpha, beta=self.beta, piT=self.piT)
            periodseries['Inflation'] = inflation
            #cb response, finds PC where expected inflation = equilibrium output
            #then find that pc intersect with MR and that output is optimal bargaining gap
            #piE = df.loc[period - 1]['Inflation']
            cbresponsei = self.ratelist[period-1]
            periodseries['Lending nom i.r.'] = cbresponsei 
            periodseries['Lending real i.r.'] = cbresponsei - inflation
            periodseries['A'] = self.A

            df.loc[period] = periodseries
            period += 1
        return df.round(4)

if __name__ == '__main__':
    l = [0, 0 , 0, 0, 0, 5, 6, 7]

    sim = CEInteractivesim(l, 
        rstar=0, 
        alpha=1,
        a = 2,
        piT=0
    )
    print(sim.DemandShock(3, temporary=True))