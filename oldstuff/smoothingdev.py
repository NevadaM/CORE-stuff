## consumption smoothing 
# takes income per period, creates its own random shocks expected and unexpected
# returns optimal consumption path
# WORKS WITH INTEREST RATE !!!
# does not work with discounting - i'm struggling trying to implement it in a way that makes sense, especially considering i'm not doing the calculations in the correct way
# I could try implementing it as some sort of adaptation of the euler equation
# or, now that consumption is being calculated each period, could try and discount it post-calculation
# this is assuming utility function is 1/(1+rho)^t * C_t
# problem is, this doesn't lead to the standard property of c_t = c_t+i for all i when r = rho
# and i still don't like the idea of doing (1 + r)/(1+rho) ^ t  *  C_t
# i just don't believe in r affecting consumption like that
# it suggests at higher interest rates, agents consume more per period
# theoretically could say yeah because you're getting more from savings - but in the model that's not how interest propogates to consumption
# and agent is smoothing, so why would they be changing consumption per period anyway???
# that is unless we go for a utility-smoothing approach
# here discounting would be like a physical tax on future consumption
# i don't like that and don't think it would be correct to implement, so will do some more research on it


import random
import numpy as np
import matplotlib.pyplot as plt


INCOME_PER_PERIOD = 100
PERIODS = 10
ASSETS = 0
R = 0.25 ##do this as a float - e.g. if 1%, write 0.01
###################################################################### THIS DON'T WORK (READ ABOVE)
RHO = 0.0 
######################################################################

random.seed(123)

#calculate lifetime income and use it to get consumption per period
def getConsumption(assets: float, expectedincomepath: list, periodevaluated: int, interestrate: float = R) -> float:
    # print(assets)
    restoflife = expectedincomepath[periodevaluated-1: ]
    # incomesum = 0
    # i = 0
    # for y in restoflife:
    #     # incomesum += (y / ((1+interestrate) ** i)) ##### in equations for lifetime wealth, this is how sum of income is measured, but i think it's really stupid for r to affect income
    #     incomesum += (y)
    #     i += 1
    incomesum = sum(restoflife)
    # lifetimeincome = ((1+interestrate) * assets) + incomesum
    lifetimeincome = assets + incomesum
    c1 = lifetimeincome / len(restoflife)
    assetsum = assets
    interestsum = 0
    for y in restoflife:
        periodassets = y - c1
        assetsum += periodassets
        interest = interestrate * (assetsum)
        interestsum += interest
        assetsum *= (1+interestrate)
    c1 += (interestsum / len(restoflife))
    return round(c1, 4)


#generate four random numbers to be four shock income values, expected or unexpected (making them divisible by five so they look nicer)
randis = random.sample(range(75, 125, 5), k=3)

#generate two random numbers to be 2 different expected shocks in first half
randpsexpected = random.sample(range(2, 7), k=2)
#and one random number for 1 unexpected shock, in second half
randpsunexpected = random.sample(range(7, 11), k=1)


#SHOCKS - {period: income}
expected = {randpsexpected[0]: randis[0], randpsexpected[1]: randis[1]}
unexpected = {randpsunexpected[0]: randis[2]} #randps[3]: randis[3]
# expected = {1: 100, 2: 100}
# unexpected = {5: 80}
unexpectedperiods = list(unexpected.keys())

#anticipated income path from p0
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
consumption = getConsumption(assets, expectedincomepath, period)
while period <= PERIODS:
    assets = assets * (1+R)
    if period in unexpectedperiods:
        expectedincomepath[period-1] = unexpected[period]
        #assetspath = np.array(expectedincomepath[:period-1]) - np.array(consumptionpath[:period-1])
        # for t in assetspath:
        #     assets += t
        #     assets *= (1+R)
    consumption = getConsumption(assets, expectedincomepath, period)
    assetpath.append(expectedincomepath[period-1] - consumption)
    consumptionpath.append(consumption)
    assets = sum(assetpath)
    period += 1

print(f'Rate of Interest: {R * 100}%')
print('Initial income path: ', initialincomepath)
print('Expected Shocks (period: shock income): ', expected)
print('Unexpected Shocks (period: shock income): ', unexpected)
print('Actual income path: ', expectedincomepath)
print('Consumption Path: ', consumptionpath)
print('Asset path: ', assetpath)
print('Sum of consumption: ', round(sum(consumptionpath)))
print('Sum of assets: ', round(sum(assetpath)))

## for the plot, trying to plot lines between each set of two points - (beginning of period, value) and (end of period, same value)
## so a loop that plots point i to point i + 1
## also need to plot vertical grey dashed jumps, between (end of period (period+1), ending value) and (beginning of next period (also period+1), new value)

index = 0
while index < (PERIODS):
    plt.plot([index, index+1], [expectedincomepath[index], expectedincomepath[index]], c='b')
    plt.plot([index, index+1], [initialincomepath[index], initialincomepath[index]], c='g')
    plt.plot([index, index+1], [consumptionpath[index], consumptionpath[index]], c='r')
    
    if index != (PERIODS - 1):
        plt.plot([index+1, index+1], [expectedincomepath[index], expectedincomepath[index+1]], c='gray')
        plt.plot([index+1, index+1], [initialincomepath[index], initialincomepath[index+1]], c='gray')
        plt.plot([index+1, index+1], [consumptionpath[index], consumptionpath[index+1]], c='gray')
    index+=1

plt.show()