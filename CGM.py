import Environment
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
    CP.airCond = round(cp[0],3)
    if(CP.airCond < 16):
        CP.airCond = 0
    CP.humidifier = round(cp[1],3)
    CP.autoAlarm = round(cp[2])
    CP.light = round(cp[3])
    CP.curtain = round(cp[4])
    CP.fans = round(cp[5])


# Performance Indicator
#PICost = 0
def calPICost(airCond_, humidifier_, autoAlarm_, light_, fans_):
    # airCond
    if(airCond_ < 16):
        airCond = 0
    else: 
        airCond = airCond_
    # humidifier
    humidifier = humidifier_
    # light
    if(light_ < 0.5):
        light = 0
    else: 
        light = 1
    # autoalarm
    if(autoAlarm_ < 0.5):
        autoAlarm = 0
    else: 
        autoAlarm = 1
    # fans
    if(fans_ < 0.5):
        fans = 0
    else:
        fans = 1
    
    cost = 0
    if(airCond != 0):
        cost += 50
    if(humidifier >= 0.3):
        cost += 5
    if(autoAlarm != 0):
        cost += 5
    if(light != 0):
        cost += 5
    if(fans != 0):
        cost += 10
    return cost

#PILight = 0
def calPILight(light_, curtain_):
    if(light_ < 0.5):
        light = 0
    else: 
        light = 1
    
    if(curtain_ < 0.5):
        curtain = 0
    else:
        curtain = 1
    time = Environment.time.state
    lighting = Environment.lighting.state
    if(light == 1):
        PILight = 100
    else: 
        if(time > 6 and time < 18):
            if(curtain == 0):
                PILight = lighting
            else:
                PILight = lighting / 2
        else:
            PILight = 20
    return PILight

#PITemp = 0
def calPITemp(airCond_, fan_):
    if(airCond_ < 16):
        airCond = 0
    else: 
        airCond = airCond_
    if(airCond != 0):
        return airCond
    else:
        if(fan_ > 0.5):
            return Environment.temperature.state - 2
        else:
            return Environment.temperature.state


def calPIMoist(humidifier_):
    if(humidifier_ < 0.3):
        return Environment.moisture.state
    else:
        return humidifier_
    
def calPINoise(window_):
    if(window_ < 0.5):
        return max(0, Environment.noise.state - 30)
    else:
        return Environment.noise.state
    

# Softgoal Weights [Budget, Light, Comfort]
W = [0.33, 0.33, 0.33]
CW = dict()
CW['userAct_0'] = np.array([[1,0.33,0.2],[3,1,0.33],[5,3,1]])   # normal
CW['userAct_1'] = np.array([[1,0.2,0.2],[5,1,0.33],[5,3,1]])    # work
CW['userAct_2'] = np.array([[1,0.2,0.2],[5,1,3],[5,0.33,1]])    # sleep
CW['userAct_3'] = np.array([[1,10,10],[0.1,1,1],[0.1,1,1]])       # none
CW['climate_0'] = np.array([[1,0.33,0.14],[3,1,0.33],[7,3,1]])  # climate hot
CW['climate_1'] = np.array([[1,0.33,0.33],[3,1,0.33],[3,3,1]])  # climate good


# Quality Constraint
budgetThreshold = 100
def SGBudgetQC(PICost_):
    if(PICost_ > budgetThreshold):
        return 0
    else:
        return 1 - PICost_ / budgetThreshold

lightThreshold = 100
def SGLightQC(PILight_):
    #PILight = calPILight()
    userAct = Environment.userAct.state
    if(userAct == 0 or userAct == 1):
        return PILight_ / lightThreshold
    else:
        return 1 - PILight_ / lightThreshold

tempL = 20
tempU = 26
moistL = 0.4
moistU = 0.7
def SGComfortQC(PITemp_, PIMoist_):
    #PITemp = calPITemp()

    if(PITemp_ >= tempL and PITemp_ <= tempU):
        comfort1 = 1
    elif(PITemp_ < tempL):
        comfort1 = PITemp_ / tempL
    else:
        comfort1 = 1 - (PITemp_ - tempU) / 10

    if(PIMoist_ >= moistL and PIMoist_ <= moistU):
        comfort2 = 1
    elif(PIMoist_ < moistL):
        comfort2 = PIMoist_ / moistL
    else:
        comfort2 = 1 - (PIMoist_ - moistU) / (1 - moistU)

    return comfort1 * 0.7 + comfort2 * 0.3   

noiseThreshold = 45
def SGNoiseQC(PINoise_):
    if(PINoise_ < noiseThreshold):
        return 1 - 0.2 * PINoise_ / noiseThreshold
    else:
        return 1.6 - 0.8 * PINoise_ / noiseThreshold


