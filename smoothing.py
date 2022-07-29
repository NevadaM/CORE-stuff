## consumption smoothing 
# takes income per period, creates its own random shocks expected and unexpected
# returns optimal consumption path
# so far only works with no interest rates
# DOES WORK WITH DISCOUNTING THO
# TODO        - DOESN'T WORK WITH INTEREST RATES - I think there's something wrong with evaluating consumption per period, iniitially decides to just save tons, then on expected shock, 
                                                #  it reevaluates and realises yo I have loads of assets (maybe from interest?) and boosts c massively
                                                #  can't determine why it does that - just builds assets even though it doesn't expect a shock
                                                #  then spends all those assets in one go - especially easy to see when unexpected shock at period 10, size 10



import random
import numpy as np
import matplotlib.pyplot as plt

INCOME_PER_PERIOD = 100
R = 0.00 ##do this as a float - e.g. if 1%, write 0.01
DELTA = 0.01 ## same here
PERIODS = 10
ASSETS = 0

# random.seed()

#calculate lifetime income and use it to get consumption per period
def getConsumption(assets: float, expectedincomepath: list, periodevaluated: int, interestrate: float = R, discountrate: float = DELTA) -> list:
    restoflife = expectedincomepath[periodevaluated-1: ]
    incomesum = 0
    i = 0
    for y in restoflife:
        incomesum += (y / ((1+interestrate) ** i))
        # incomesum += (y)
        i += 1
    lifetimeincome = ((1+interestrate) * assets) + incomesum
    c1 = lifetimeincome / len(restoflife)
    # return round(consumptionpp, 4)
    consumptionpath = []
    j = 0
    for y in restoflife:
        consumptionpath.append(c1 * (((1+interestrate) / (1+discountrate)) ** j))
        j+=1
    return np.round(consumptionpath, 5)

#generate four random numbers to be four shock income values, expected or unexpected (making them divisible by five so they look nicer)
randis = random.sample(range(75, 125, 5), k=3)

#generate two random numbers to be 2 different expected shocks in first half
randpsexpected = random.sample(range(2, 7), k=2)
#and one random number for 1 unexpected shock, in second half
randpsunexpected = random.sample(range(7, 11), k=1)


#SHOCKS - {period: income}
expected = {randpsexpected[0]: randis[0], randpsexpected[1]: randis[1]}
unexpected = {randpsunexpected[0]: randis[2]} #randps[3]: randis[3]
unexpectedperiods = list(unexpected.keys())

#anticipated income path from p0
initialincomepath = []
for i in range(PERIODS):
    initialincomepath.append(INCOME_PER_PERIOD)
for i in expected:
    initialincomepath[i-1] = expected[i]



expectedincomepath = initialincomepath.copy()

period = 1
# consumptionpath = []
consumptionpath = getConsumption(ASSETS, expectedincomepath, period)
while period <= PERIODS:
    if period in unexpectedperiods:
        expectedincomepath[period-1] = unexpected[period]
        assetspath = np.array(expectedincomepath[:period-1]) - np.array(consumptionpath[:period-1])
        assets = ASSETS * (1+R)
        for t in assetspath:
            assets += t
            assets *= (1+R)
        consumptionpath[period-1:] = getConsumption(assets, expectedincomepath, period)
    #consumptionpath.append(consumption)
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