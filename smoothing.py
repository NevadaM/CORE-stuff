###### how easy is consumption smoothing?
# trying to model permanent income hypothesis
# over 10 periods, try to keep consumption as smooth as possible (or overall utility as great as possible i guess)
# mix of expected and unexpected shocks
# 2 expected shocks info comes before game starts
# between unexpected shocks in random periods, no shock is directly followed by another shock
# on game start with expected shock info, player chooses initial consumption
# on each period, shock or no shock, choose new consumption
# results show income path, chosen consumption path, optimal consumption path
# NO DISCOUNT RATE, NO RATE OF INTEREST (YET) - if there was, use euler eqn - if equal, Ct = r/1+r * Budget Constraint
# bydget constraint = (1+r)A(t-1) + sum(1/(1+r)^i  *  y(t+i))
# every period needs to report current debt as well
# each period has assets (savings/debt)
# period-specific change in assets = income - consumption
# let's start with no assets

# make optimal first
# expected shocks affect expected lifetime income
# given no discount rate or rate of interest, just divide by periods to find initial consumption path
# unexpected temporary shock with no rate of interest or discounting, consumption path moves up/down by half shock size and stays like that for next period to recuperate?
# unexpected permanent shock causes permanent change in consumption 

import random
import numpy as np
import matplotlib.pyplot as plt

INCOME_PER_PERIOD = 100
DELTA = 0
R = 0
PERIODS = 10
ASSETS = 0

#calculate lifetime income and use it to get consumption per period
def getConsumption(assets: float, expectedincomepath: list, periodevaluated: int) -> float:
    restoflife = expectedincomepath[periodevaluated-1: ]
    lifetimeincome = assets + sum(restoflife)
    consumptionpp = lifetimeincome / len(restoflife)
    return round(consumptionpp, 4)

#generate four random numbers to be four different periods of shocks
randps = random.sample(range(10), k=4)
#generate four random numbers to be four shock income values, expected or unexpected (making them divisible by five so they look nicer)
randis = random.sample(range(0, 200, 5), k=4)


#SHOCKS - {period: income}
expected = {randps[0]: randis[0], randps[1]: randis[1]}
unexpected = {randps[2]: randis[2], randps[3]: randis[3]}
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
consumption = getConsumption(ASSETS, expectedincomepath, 1)
while period <= PERIODS:
    if period in unexpectedperiods:
        expectedincomepath[period-1] = unexpected[period]
        assetspath = np.array(expectedincomepath[:period-1]) - np.array(consumptionpath)
        assets = sum(assetspath)
        consumption = getConsumption(assets, expectedincomepath, period)
    consumptionpath.append(consumption)
    period += 1

print('Initial income path: ', initialincomepath)
print('Actual income path: ', expectedincomepath)
print('Consumption Path: ', consumptionpath)
print(round(sum(consumptionpath), 4))
