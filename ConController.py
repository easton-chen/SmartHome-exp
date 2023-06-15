import CGM
import Environment
from scipy.optimize import minimize, Bounds, LinearConstraint, NonlinearConstraint, differential_evolution
import numpy as np

noadaptutilitydata = []

# x is CPs, [airCond, humidifier, autoalarm, light, curtain]
def utilityFun(x):
    utility = 0
    SGWeights = CGM.W
    PICost = CGM.calPICost(x[0], x[1], x[2], x[3], x[5])
    PILight = CGM.calPILight(x[3], x[4])
    PITemp = CGM.calPITemp(x[0], x[5])
    PIMoist = CGM.calPIMoist(x[1])
    utility = SGWeights[0] * CGM.SGBudgetQC(PICost) + SGWeights[1] * CGM.SGLightQC(PILight) + SGWeights[2] * CGM.SGComfortQC(PITemp, PIMoist)
    return -1.0 * utility

def analysis():
    #context = Environment.context
    pass
        
  
# bounds can be param, to make sure goal
def plan(bounds):
    '''
    x0 = np.array([0,0,1])
    bounds = Bounds([0,30],[0,1],[0,1])
    constraints = (
        {'type':'ineq', 'fun': lambda x: x[0] - 0},\
        {'type':'ineq', 'fun': lambda x: -x[0] + 30},\
        {'type':'ineq', 'fun': lambda x: x[1] + 0},\
        {'type':'ineq', 'fun': lambda x: -x[1] + 1},\
        {'type':'ineq', 'fun': lambda x: x[2] + 0},\
        {'type':'ineq', 'fun': lambda x: -x[2] + 1}
    )
    res = minimize(utilityFun, x0, method='trust-constr', constraints=constraints)
    '''
    
    res = differential_evolution(utilityFun, bounds)
    return res
    #print(-1 * res.fun)
    #print(res.x)

# CP: airCond, humidifier, autoalarm, light, curtain, fans 
def run():
    bounds = [(0,30), (0,1), (0,1), (0,1), (0,1), (0,1)]
    flag = False
    if(Environment.userAct.state == 3):
        bounds[2] = (1,1)
        flag = True
    if(Environment.network.state == 0):
        bounds[0] = (0,0)
        flag = True
    
    res = plan(bounds)
    curUtility = -1 * utilityFun([CGM.CP.airCond, CGM.CP.humidifier, CGM.CP.autoAlarm, CGM.CP.light, CGM.CP.curtain, CGM.CP.fans])
    #noadaptutilitydata.append(curUtility)
    calUtility = -1 * res.fun
    if(curUtility < calUtility):
        print("Adaptation for better utility!!! curU: " + str(curUtility) + ", calU:" + str(calUtility))
        print(res.x)
        CGM.setCP(res.x)
    elif(flag):
        print("Adaptation for context constraint!")
        CGM.setCP(res.x)


if __name__ == '__main__':
    run()
    