import CGM
from Environment import env
import MPCController
from MPCAdaptor import MPCAdaptor
import numpy as np 
import matplotlib.pyplot as plt

utilitydata = []
cpdata = []
pidata = []

def collectStat():
    CP = CGM.CP
    PI = CGM.PI

    cpdata.append([CP.airCond, CP.fans, CP.humidifier, CP.curtain, CP.light, CP.autoAlarm])
    pidata.append([PI.PICost, PI.PITemp, PI.PIMoist, PI.PILight])

    SGBudget = CGM.SGBudgetQC(PI.PICost)
    SGLight = CGM.SGLightQC(PI.PILight)
    SGComfort = CGM.SGComfortQC(PI.PITemp, PI.PIMoist)

    print("SG quality:" + str(SGBudget) + "," + str(SGComfort) + "," + str(SGLight))

    utility = CGM.W[0] * SGBudget + CGM.W[1] * SGLight + CGM.W[2] * SGComfort

    utilitydata.append(utility)

def runexp1():
    timeLimit = 48
    t = 0
    #x_p = np.array([0, MPCController.Env.tempList[0], MPCController.Env.moistList[0], 0]).reshape(-1,1)
    #print("init x:" + str(x_p))
    
    #cpList = []
    #piList = []
    CGM.PI.PICost = 0
    CGM.PI.PITemp = env.tempList[0]
    CGM.PI.PIMoist = env.moistList[0]
    CGM.PI.PILight = env.lightList[0]
    
    for t in range(timeLimit):
        print("t:" + str(t))
        x_p = np.array([CGM.PI.PICost, CGM.PI.PITemp, CGM.PI.PIMoist, CGM.PI.PILight])

    # update environment
        env.update(t)
    # whether adapt mpc setting or not
        MPCController.mpcAdapt(x_p, t)
        #if(t == 24):
            #MPCController.mpcAdaptTest(x_p)
    
    # mpc control 
        u0 = MPCController.plan(x_p)
        
    # effect control to system
        #print(u0)
        u = [0,0,0,0,0,0]
        for i in range(len(u0)):
            u[i] = u0[i][0]
        CGM.setCP(u)
        CGM.setPI(env)
        
        collectStat()
    
def plotResult():    
    x = np.arange(0,48)

    fig = plt.figure(num=1, figsize=(8, 8)) 
    numplot = 5
    ax1 = fig.add_subplot(numplot,1,1)
    ax2 = fig.add_subplot(numplot,1,2)
    ax3 = fig.add_subplot(numplot,1,3)
    ax4 = fig.add_subplot(numplot,1,4)
    ax5 = fig.add_subplot(numplot,1,5)

    pidata_ = pidata[:48]
    cpdata_ = cpdata[:48]
    utilitydata_ = utilitydata[:48]

    cvMoist = np.array(env.moistList[:48])
    piMoist = np.array([row[2] for row in pidata_])
    cpHumi = np.array([row[2] for row in cpdata_])
    ax1.plot(x, cvMoist, label='outside moist', linestyle=':')
    ax1.plot(x, piMoist, label='moist', linestyle=':')
    ax1.set_yticks((0,0.25,0.5,0.75,1)) 
    ax1.legend(loc=(1.03,0.75)) 
    ax1.spines['right'].set_visible(False)
    ax1_ = ax1.twinx()
    ax1_.plot(x, cpHumi, color='red', label='humi')
    ax1_.set_yticks((0, 1, 2, 3))
    ax1_.legend(loc=(1.04,0.25))

    cvTemp = np.array(env.tempList[:48])
    piTemp = np.array([row[1] for row in pidata_])
    cpAc = np.array([row[0] for row in cpdata_])
    cpFan = np.array([row[1] for row in cpdata_])
    ax2.plot(x, cvTemp, label='outside temp', linestyle=':')
    ax2.plot(x, piTemp, label='temp', linestyle=':')
    ax2.set_yticks((10,15,20,25,30,35))
    ax2.legend(loc=(1.03,0.75)) 
    ax2.spines['right'].set_visible(False)
    ax2_ = ax2.twinx()
    ax2_.plot(x, cpAc, color='red', label='ac')
    ax2_.plot(x, cpFan, label='fan')
    ax2_.set_yticks((0, 1, 2, 3))
    ax2_.legend(loc=(1.04,0.25))

    cvLight = np.array(env.lightList[:48])
    piLight = np.array([row[3] for row in pidata_])
    ax3.plot(x, cvLight, label='outside Light', linestyle=':')
    ax3.plot(x, piLight, label='light', linestyle=':')
    ax3.set_yticks((0,25,50,75,100))
    ax3.legend(loc=(1.03,0.75)) 

    piCost = np.array([row[0] for row in pidata_])
    ax4.plot(x, piCost, label='cost', linestyle=':')
    ax4.set_yticks((0,25,50,75,100))
    ax4.legend(loc=(1.03,0.75)) 

    utility = np.array(utilitydata_)
    ax5.plot(x, utility, label='utility', linestyle=':')
    #ax2.plot(x, y10, label='utility wo adaptation', linestyle=':')
    ax5.set_yticks((0,0.2,0.4,0.6,0.8,1))
    ax5.legend(loc=(1.03,0.75)) 

    plt.subplots_adjust(left=0.1, right=0.7, bottom=0.1, top=0.9)

    plt.show()

    avgU = np.mean(utility)
    print("avgU:" + str(avgU))

def runexp2():
    timeLimit = 48
    t = 0

    CGM.PI.PICost = 0
    CGM.PI.PITemp = env.tempList[0]
    CGM.PI.PIMoist = env.moistList[0]
    CGM.PI.PILight = env.lightList[0]
    
    for t in range(timeLimit):
        print("t:" + str(t))
        x_p = np.array([CGM.PI.PICost, CGM.PI.PITemp, CGM.PI.PIMoist, CGM.PI.PILight])

    # update environment
        env.update(t)
    # no adapt mpc 
        #MPCController.mpcAdapt(x_p, t)
        MPCController.mpcAdapt2(x_p, t)
    
    # mpc control 
        u0 = MPCController.plan(x_p)
        
    # effect control to system
        #print(u0)
        if(env.conn == 0):
            u0[0][0] = 0
        u = [0,0,0,0,0,0]
        for i in range(len(u0)):
            u[i] = u0[i][0]
        CGM.setCP(u)
        CGM.setPI(env)
        
        collectStat()

def runexp_react():
    timeLimit = 48
    t = 0

    CGM.PI.PICost = 0
    CGM.PI.PITemp = env.tempList[0]
    CGM.PI.PIMoist = env.moistList[0]
    CGM.PI.PILight = env.lightList[0]

    u = [0,0,0,0,0,0]
    for t in range(timeLimit):
        print("t:" + str(t))
        env.update(t)
        u[0] = CGM.CP.airCond
        u[1] = CGM.CP.fans
        u[2] = CGM.CP.humidifier
        u[3] = CGM.CP.curtain
        u[4] = CGM.CP.light
        u[5] = CGM.CP.autoAlarm

        if(CGM.PI.PITemp > 28):
            if(u[0] < 3):
                u[0] = u[0] + 1
            elif(u[1] < 3):
                u[1] = u[1] + 1
        elif(CGM.PI.PITemp < 22):
            u[0] = 0
            u[1] = 0
        
        if(CGM.PI.PIMoist < 0.5):
            if(u[2] < 3):
                u[2] = u[2] + 1
        elif(CGM.PI.PIMoist > 0.7):
            u[2] = 0

        if(CGM.PI.PILight < 75):
            u[4] = 1
        CGM.setCP(u)
        CGM.setPI(env)

        collectStat()


    
if __name__ == '__main__':
    runexp2()
    plotResult()    