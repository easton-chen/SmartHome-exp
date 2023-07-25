from Environment import env
import numpy as np

# Control Parameters
class ControlParam:
    def __init__(self):
        self.airCond = 0
        self.humidifier = 0
        self.autoAlarm = 0
        self.light = 0
        self.curtain = 0
        self.fans = 0

CP = ControlParam()
def setCP(cp):
    CP.airCond = round(cp[0])
    CP.fans = round(cp[1])
    CP.humidifier = round(cp[2])
    CP.curtain = round(cp[3])
    CP.light = round(cp[4])
    CP.autoAlarm = round(cp[5])
    


class PerformanceIndicator:
    def __init__(self):
        self.PICost = 0
        self.PILight = 0
        self.PITemp = 0
        self.PIMoist = 0

    def setPICost(self, CP):
        cost = 25 * CP.airCond + 5 * CP.humidifier + 5 * CP.autoAlarm + 2 * CP.light + 5 * CP.fans
        self.PICost = cost
    
    def setPITemp(self, CP, Env):
        temp = self.PITemp
        setTemp = 25
        envTemp = Env.temp
        self.PITemp = temp + 0.6 * CP.airCond * (setTemp - temp) - 0.2 * CP.fans + 0.5 * (envTemp - temp)

    def setPIMoist(self, CP, Env):
        moist = self.PIMoist
        maxMoist = 1
        envMoist = Env.moist
        self.PIMoist = moist + 0.1 * CP.humidifier * (maxMoist - moist) + 0.03 * (envMoist - moist)
        self.PIMoist = min(maxMoist, self.PIMoist)
        self.PIMoist = max(0, self.PIMoist)

    def setPILight(self, CP, Env):
        light = self.PILight
        envLight = Env.light
        self.PILight = envLight + 1 * CP.light * (100 - envLight) - 20 * CP.curtain
        self.PILight = min(100, self.PILight)
        self.PILight = max(10, self.PILight)

PI = PerformanceIndicator()
def setPI(env):
    PI.setPICost(CP)
    PI.setPITemp(CP, env)
    PI.setPIMoist(CP, env)
    PI.setPILight(CP, env)


# Softgoal Weights [Budget, Light, Comfort]
W = [0.33, 0.33, 0.33]
CW = dict()
CW['userAct_0'] = np.array([[1,0.33,0.2],[3,1,0.33],[5,3,1]])   # normal
CW['userAct_1'] = np.array([[1,0.2,0.2],[5,1,0.33],[5,3,1]])    # work
CW['userAct_2'] = np.array([[1,0.2,0.2],[5,1,3],[5,0.33,1]])    # sleep
CW['userAct_3'] = np.array([[1,10,10],[0.1,1,1],[0.1,1,1]])       # none
CW['climate_0'] = np.array([[1,0.33,0.14],[3,1,0.33],[7,3,1]])  # climate hot
CW['climate_1'] = np.array([[1,0.33,0.33],[3,1,0.33],[3,3,1]])  # climate good


# Quality Function
budgetThreshold = 100
def SGBudgetQC(PICost_):
    if(PICost_ > budgetThreshold):
        return 0
    else:
        return 1 - PICost_ / budgetThreshold

lightThreshold = 100
def SGLightQC(PILight_):
    #PILight = calPILight()
    userAct = env.userAct
    if(userAct == 1 or userAct == 2):
        return PILight_ / lightThreshold
    else:
        return 1 - PILight_ / lightThreshold

tempL = 24
tempU = 26
moistL = 0.4
moistU = 0.6
def SGComfortQC(PITemp_, PIMoist_):
   
    if(PITemp_ >= tempL and PITemp_ <= tempU):
        comfort1 = 1
    elif(PITemp_ < tempL):
        comfort1 = max(PITemp_ / tempL, 0)
    else:
        comfort1 = max(1 - (PITemp_ - tempU) / 10, 0)

    if(PIMoist_ >= moistL and PIMoist_ <= moistU):
        comfort2 = 1
    elif(PIMoist_ < moistL):
        comfort2 = PIMoist_ / moistL
    else:
        comfort2 = 1 - (PIMoist_ - moistU) / (1 - moistU)

    return comfort1 * 0.6 + comfort2 * 0.4   

noiseThreshold = 45
def SGNoiseQC(PINoise_):
    if(PINoise_ < noiseThreshold):
        return 1 - 0.2 * PINoise_ / noiseThreshold
    else:
        return 1.6 - 0.8 * PINoise_ / noiseThreshold


