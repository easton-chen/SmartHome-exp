import CGM
from Environment import env
import MPCController
import numpy as np 
import matplotlib.pyplot as plt

utilitydata = []
cpdata = []
pidata = []

def collectStat(u0, x_p):
    CP = CGM.CP
    PI = CGM.PI

    cpdata.append([CP.airCond,CP.fans,CP.humidifier,CP.curtain,CP.light,CP.autoAlarm])
    pidata.append(x_p)

    SGBudget = CGM.SGBudgetQC(PI.PICost)
    SGLight = CGM.SGLightQC(PI.PILight)
    SGComfort = CGM.SGComfortQC(PI.PITemp, PI.PIMoist)

    utility = CGM.W[0] * SGBudget + CGM.W[1] * SGLight + CGM.W[2] * SGComfort

    utilitydata.append(utility)

def runexp1():
    timeLimit = 48
    t = 0
    x_p = np.array([0, MPCController.Env.tempList[0], MPCController.Env.moistList[0], 0]).reshape(-1,1)
    
    #cpList = []
    #piList = []
    
    for i in range(timeLimit):
    # update environment
        env.update(t)
    # whether adapt mpc setting or not
        #MPCController.mpcAdapt(x_p, t)
        if(t == 24):
            MPCController.mpcAdaptTest(x_p)
    
    # mpc control 
        u0, x_p = MPCController.plan(x_p)
        #cpList.append(u0)
        #piList.append(x_p)
    # effect control to system
        #print(u0)
        CGM.setCP(u0)
        CGM.setPI(env)

        collectStat(u0, x_p)
        t = t + 1
    
def plotResult():    
    x = np.arange(0,48)

    fig = plt.figure(num=1, figsize=(8, 8)) 
    numplot = 5
    ax1 = fig.add_subplot(numplot,1,1)
    ax2 = fig.add_subplot(numplot,1,2)
    ax3 = fig.add_subplot(numplot,1,3)
    ax4 = fig.add_subplot(numplot,1,4)
    ax5 = fig.add_subplot(numplot,1,5)

    cvMoist = np.array(env.moistList[:48])
    piMoist = np.array([row[2] for row in pidata])
    cpHumi = np.array([row[2] for row in cpdata])
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
    piTemp = np.array([row[1] for row in pidata])
    cpAc = np.array([row[0] for row in cpdata])
    cpFan = np.array([row[1] for row in cpdata])
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
    piLight = np.array([row[3] for row in pidata])
    ax3.plot(x, cvLight, label='outside Light', linestyle=':')
    ax3.plot(x, piLight, label='light', linestyle=':')
    ax3.set_yticks((0,25,50,75,100))
    ax3.legend(loc=(1.03,0.75)) 

    piCost = np.array([row[0] for row in pidata])
    ax4.plot(x, piCost, label='cost', linestyle=':')
    ax4.set_yticks((0,25,50,75,100))
    ax4.legend(loc=(1.03,0.75)) 

    utility = np.array(utilitydata)
    ax5.plot(x, utility, label='utility', linestyle=':')
    #ax2.plot(x, y10, label='utility wo adaptation', linestyle=':')
    ax5.set_yticks((0,0.2,0.4,0.6,0.8,1))
    ax5.legend(loc=(1.03,0.75)) 

    plt.subplots_adjust(left=0.1, right=0.7, bottom=0.1, top=0.9)

    plt.show()
    
if __name__ == '__main__':
    runexp1()
    plotResult()