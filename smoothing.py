import random
import matplotlib.pyplot as plt

def getConsumption(assets: float, expectedincomepath: list, periodevaluated: int, interestrate: float) -> float:
    print(assets)
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

class Smoothing():
    def __init__(self, INCOME_PER_PERIOD, PERIODS, ASSETS, R) -> None:
        self.PERIODS = PERIODS
        self.R = R

        randis = random.sample(range(75, 125, 5), k=3)
        randpsexpected = random.sample(range(2, 7), k=2)
        randpsunexpected = random.sample(range(7, 11), k=1)

        expected = {randpsexpected[0]: randis[0], randpsexpected[1]: randis[1]}
        unexpected = {randpsunexpected[0]: randis[2]} 
        unexpectedperiods = list(unexpected.keys())
        
        initialincomepath = []
        for i in range(PERIODS):
            initialincomepath.append(INCOME_PER_PERIOD)
        for i in expected:
            initialincomepath[i-1] = expected[i]

        expectedincomepath = initialincomepath.copy()

        period = 1
        assetpath = [ASSETS]
        assets = ASSETS
        consumptionpath = []
        consumption = getConsumption(assets, expectedincomepath, period, R)
        while period <= PERIODS:
            assets = assets * (1+R)
            if period in unexpectedperiods:
                expectedincomepath[period-1] = unexpected[period]
            consumption = getConsumption(assets, expectedincomepath, period, R)
            assetpath.append(expectedincomepath[period-1] - consumption)
            consumptionpath.append(consumption)
            assets = sum(assetpath)
            period += 1

        self.initialincomepath = initialincomepath
        self.expectedincomepath = expectedincomepath
        self.consumptionpath = consumptionpath
        self.assetpath = assetpath
        self.expected = expected
        self.unexpected = unexpected


    def PrintStuff(self) -> None:
        print(f'Rate of Interest: {self.R * 100}%')
        print('Initial income path: ', self.initialincomepath)
        print('Expected Shocks (period: shock income): ', self.expected)
        print('Unexpected Shocks (period: shock income): ', self.unexpected)
        print('Actual income path: ', self.expectedincomepath)
        print('Consumption Path: ', self.consumptionpath)
        print('Asset path: ', self.assetpath)
        print('Sum of consumption: ', round(sum(self.consumptionpath)))
        print('Sum of assets: ', round(sum(self.assetpath)))

    def PlotStuff(self):
        index = 0
        while index < (self.PERIODS):
            plt.plot([index, index+1], [self.expectedincomepath[index], self.expectedincomepath[index]], c='b')
            plt.plot([index, index+1], [self.initialincomepath[index], self.initialincomepath[index]], c='g')
            plt.plot([index, index+1], [self.consumptionpath[index], self.consumptionpath[index]], c='r')
            
            if index != (self.PERIODS - 1):
                plt.plot([index+1, index+1], [self.expectedincomepath[index], self.expectedincomepath[index+1]], c='gray')
                plt.plot([index+1, index+1], [self.initialincomepath[index], self.initialincomepath[index+1]], c='gray')
                plt.plot([index+1, index+1], [self.consumptionpath[index], self.consumptionpath[index+1]], c='gray')
            index+=1

        plt.show()