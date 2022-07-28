## consumption smoothing 
# takes income per period, creates its own random shocks expected and unexpected
# returns optimal consumption path
# so far only works with no impatience/discounting
# suggestions - could make more simple to read by making expected shocks happen in first half, unexpected in second ?


import random
import numpy as np
import matplotlib.pyplot as plt

INCOME_PER_PERIOD = 100
R = 0.0
PERIODS = 10
ASSETS = 0

#calculate lifetime income and use it to get consumption per period
def getConsumption(assets: float, expectedincomepath: list, periodevaluated: int, interestrate: float = R) -> float:
    restoflife = expectedincomepath[periodevaluated-1: ]
    incomesum = 0
    i = 0
    for y in restoflife:
        incomesum += (1 / ((1+interestrate) ** i)) * y
        i += 1
    lifetimeincome = ((1+interestrate) * assets) + incomesum
    consumptionpp = lifetimeincome / len(restoflife)
    return round(consumptionpp, 4)

#generate four random numbers to be four different periods of shocks
randps = random.sample(range(2, 11), k=3)
#generate four random numbers to be four shock income values, expected or unexpected (making them divisible by five so they look nicer)
randis = random.sample(range(75, 125, 5), k=3)


#SHOCKS - {period: income}
expected = {randps[0]: randis[0], randps[1]: randis[1]}
unexpected = {randps[2]: randis[2]} #randps[3]: randis[3]
unexpectedperiods = list(unexpected.keys())

#anticipated income path from p0
initialincomepath = []
for i in range(PERIODS):
    initialincomepath.append(INCOME_PER_PERIOD)
for i in expected:
    initialincomepath[i-1] = expected[i]



expectedincomepath = initialincomepath.copy()

period = 1
consumptionpath = []
consumption = getConsumption(ASSETS, expectedincomepath, period)
while period <= PERIODS:
    if period in unexpectedperiods:
        expectedincomepath[period-1] = unexpected[period]
        assetspath = np.array(expectedincomepath[:period-1]) - np.array(consumptionpath)
        assets = 0
        for t in assetspath:
            assets += t
            assets *= (1+R)
        consumption = getConsumption(assets, expectedincomepath, period)
    consumptionpath.append(consumption)
    period += 1

print(f'Rate of Interest: {R * 100}%')
print('Initial income path: ', initialincomepath)
print('Expected Shocks (period: shock income): ', expected)
print('Unexpected Shocks (period: shock income): ', unexpected)
print('Actual income path: ', expectedincomepath)
print('Consumption Path: ', consumptionpath)
print(round(sum(consumptionpath)))

## for the plot, trying to plot lines between each set of two points - (beginning of period, value) and (end of period, same value)
## so a loop that plots point i to point i + 1
## also need to plot vertical grey dashed jumps, between (end of period (period+1), ending value) and (beginning of next period (also period+1), new value)

index = 0
while index < (PERIODS):
    plt.plot([index, index+1], [consumptionpath[index], consumptionpath[index]], c='r')
    plt.plot([index, index+1], [expectedincomepath[index], expectedincomepath[index]], c='b')
    plt.plot([index, index+1], [initialincomepath[index], initialincomepath[index]], c='g')
    
    if index != 9:
        plt.plot([index+1, index+1], [consumptionpath[index], consumptionpath[index+1]], c='gray')
        plt.plot([index+1, index+1], [expectedincomepath[index], expectedincomepath[index+1]], c='gray')
        plt.plot([index+1, index+1], [initialincomepath[index], initialincomepath[index+1]], c='gray')
    index+=1

plt.show()