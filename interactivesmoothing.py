# now want to do smoothing but takes a list of inputs that are like a history
# idea is each period, player chooses consumption and this gets added to list and plotted
# initially at period 0, get presented with expected income path and choose a consumption per period
# then at unexpected shocks, present new expected income path and ask to choose a new consumption per period
# finally return what was optimal

# this is gonna need the expected income path logic, unexpected shock logic, integration of agent choices and more
import matplotlib.pyplot as plt
import random


def getConsumption(assets: float, expectedincomepath: list, periodevaluated: int, interestrate: float) -> float:
    restoflife = expectedincomepath[periodevaluated-1: ]
    incomesum = sum(restoflife)
    lifetimeincome = assets + incomesum
    c1 = lifetimeincome / len(restoflife)
    interestsum = 0
    for y in restoflife:
        interest = interestrate * (y - c1)
        interestsum += interest
    c1 += (interestsum / len(restoflife))
    return round(c1, 4)

class InteractiveSmoothing:
    def __init__(
        self, 
        l: list,
        INCOME_PER_PERIOD: int = 100, 
        PERIODS: int = 20, 
        ASSETS: int = 0, 
        R: float = 0) -> None:

        '''TODO -> change hardcoded ranges for random generation'''

        self.PERIODS = PERIODS
        self.R = R
        self.ASSETS = ASSETS

        # random.seed(1234)

        randis = random.sample(range(75, 125, 5), k=4) #HARDCODED
        randpsexpected = random.sample(range(2, 15), k=2) #HARDCODED
        randpsunexpected = random.sample(range(6, 21), k=2) #HARDCODED

        self.expected = {randpsexpected[0]: randis[0], randpsexpected[1]: randis[1]} #HARDCODED
        self.unexpected = {randpsunexpected[0]: randis[2], randpsunexpected[1]: randis[3]} #HARDCODED
        # self.unexpected = {6: 120}
        self.unexpectedperiods = list(self.unexpected.keys())
        
        self.initialincomepath = []
        for i in range(PERIODS):
            self.initialincomepath.append(INCOME_PER_PERIOD)
        for i in self.expected:
            self.initialincomepath[i-1] = self.expected[i]

        self.consumptionpath = l
        self.optimalpath = self.getOptimalPath()

    def getOptimalPath(self):
        self.expectedincomepath = self.initialincomepath.copy()
        period = 1
        assetpath = [self.ASSETS]
        assets = self.ASSETS
        consumptionpath = []
        consumption = getConsumption(assets, self.expectedincomepath, period, self.R)
        while period <= self.PERIODS:
            assets = assets * (1+self.R)
            if period in self.unexpectedperiods:
                self.expectedincomepath[period-1] = self.unexpected[period]
            consumption = getConsumption(assets, self.expectedincomepath, period, self.R)
            assetpath.append(self.expectedincomepath[period-1] - consumption)
            consumptionpath.append(consumption)
            assets = sum(assetpath)
            period += 1
        
        return consumptionpath
        
    def PlotAll(self, plot_optimal=False, plot_unexpected=False):
        index = 0
        while index < len(self.consumptionpath):
            plt.plot([index, index+1], [self.initialincomepath[index], self.initialincomepath[index]], c='g')
            plt.plot([index, index+1], [self.consumptionpath[index], self.consumptionpath[index]], c='r')
            if index != len(self.consumptionpath) - 1:
                plt.plot([index+1, index+1], [self.initialincomepath[index], self.initialincomepath[index+1]], c='gray')
            if plot_optimal:
                plt.plot([index, index+1], [self.optimalpath[index], self.optimalpath[index]], c='pink')
                if index != len(self.consumptionpath) - 1:
                    plt.plot([index+1, index+1], [self.optimalpath[index], self.optimalpath[index+1]], c='gray')
            if plot_unexpected:
                if index+1 in self.unexpectedperiods:
                    plt.plot([index+1, index+2], [self.unexpected[index+1], self.unexpected[index+1]], c='b')
                    plt.plot([index+1, index+1], [self.initialincomepath[index], self.unexpected[index+1]], c='gray')
                    if index != len(self.consumptionpath) - 2:
                        plt.plot([index+2, index+2], [self.initialincomepath[index+2], self.unexpected[index+1]], c='gray')

            if index != (len(self.consumptionpath) - 1):
               # plt.plot([index+1, index+1], [self.expectedincomepath[index], self.expectedincomepath[index+1]], c='gray')
                plt.plot([index+1, index+1], [self.consumptionpath[index], self.consumptionpath[index+1]], c='gray')
            index+=1
        while index < (self.PERIODS):
            #plt.plot([index, index+1], [self.expectedincomepath[index], self.expectedincomepath[index]], c='b')
            plt.plot([index, index+1], [self.initialincomepath[index], self.initialincomepath[index]], c='g')
            if plot_optimal:
                plt.plot([index, index+1], [self.optimalpath[index], self.optimalpath[index]], c='pink')
            
            if index != (self.PERIODS - 1):
               # plt.plot([index+1, index+1], [self.expectedincomepath[index], self.expectedincomepath[index+1]], c='gray')
                plt.plot([index+1, index+1], [self.initialincomepath[index], self.initialincomepath[index+1]], c='gray')
                if plot_optimal:
                    plt.plot([index+1, index+1], [self.optimalpath[index], self.optimalpath[index+1]], c='gray')
            index+=1

        plt.show()

    def PlotInitial(self):
        index = 0
        while index < (self.PERIODS):
            plt.plot([index, index+1], [self.initialincomepath[index], self.initialincomepath[index]], c='g')
            
            if index != (self.PERIODS - 1):
                plt.plot([index+1, index+1], [self.initialincomepath[index], self.initialincomepath[index+1]], c='gray')
            index+=1

        plt.show()


if __name__ == '__main__':
    sim = InteractiveSmoothing([90, 90, 90, 90, 80, 90])
    # sim.PlotAll(plot_unexpected=True)
    sim.PlotInitial()