import CGM
from Environment import env
import MPCController
import BaseMPCController
from MPCAdaptor import MPCAdaptor
import numpy as np 
import matplotlib.pyplot as plt
import random
import math
import pandas as pd

envdata = []

utilitydata = []
cpdata = []
pidata = []

avgUBase = []
avgU1 = []
avgU2 = []

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
    

def runexp2l():
    casenum = 20
    for i in range(casenum):
        env.loadEnv(envdata[i])
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
        utilitydata.clear()

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
        avgU2.append(np.mean(utilitydata))
    
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

def runexp1l():
    casenum = 20
    for i in range(casenum):
        env.loadEnv(envdata[i])
        timeLimit = 48
        t = 0

        CGM.PI.PICost = 0
        CGM.PI.PITemp = env.tempList[0]
        CGM.PI.PIMoist = env.moistList[0]
        CGM.PI.PILight = env.lightList[0]
        utilitydata.clear()

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

        avgU1.append(np.mean(utilitydata))

def runexpBase():
    casenum = 20
    for i in range(casenum):
        env.loadEnv(envdata[i])
        timeLimit = 48
        t = 0

        CGM.PI.PICost = 0
        CGM.PI.PITemp = env.tempList[0]
        CGM.PI.PIMoist = env.moistList[0]
        CGM.PI.PILight = env.lightList[0]

        u = [0,0,0,0,0,0]
        utilitydata.clear()
        for t in range(timeLimit):
            print("t:" + str(t))
            env.update(t)

            x_p = np.array([CGM.PI.PICost, CGM.PI.PITemp, CGM.PI.PIMoist, CGM.PI.PILight])
            u0 = BaseMPCController.plan(x_p)

            u = [0,0,0,0,0,0]
            for i in range(len(u0)):
                u[i] = u0[i][0]
            CGM.setCP(u)
            CGM.setPI(env)
            
            collectStat()

        avgUBase.append(np.mean(utilitydata))
            

def runexpReact():
    casenum = 20
    for i in range(casenum):
        env.loadEnv(envdata[i])
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
        #sum = 0
        #for i in range(len(utilitydata)):
        #    sum += utilitydata[i]
        avgU1.append(np.mean(utilitydata))

def generateEnv(exp):
    casenum = 20
    data = []
    envfile = open('env.csv','w+')

    if(exp == 1):
        for i in range(casenum):
            tempAvg = random.randint(10,35) + random.random()
            tempBias = random.randint(5,10) + random.random()
            moistAvg = random.randint(20,80) / 100
            moistBias = random.randint(5,10) / 100

            length = 48
            userActList = []
            tempList = []
            moistList = []
            lightList = []
            connList = []
            for i in range(length):
                userActList.append(1)

                tempList.append(tempBias * math.sin(((i / 2 - 8) / 12) * math.pi) + tempAvg)
                
                moistList.append(moistBias * math.sin(((i / 2 + 4) / 12) * math.pi) + moistAvg)
                
                if(i > 14 and i < 34):
                    lightList.append(random.randint(60, 100))
                elif((i >= 10 and i <= 14) or (i >= 34 and i <= 38)):
                    lightList.append(random.randint(40, 80))
                else:
                    lightList.append(10)

                connList.append(1)
            data.append([userActList, tempList, moistList, lightList, connList])
    if(exp == 2):
        for i in range(casenum):
            tempAvg = random.randint(10,35) + random.random()
            tempBias = random.randint(5,10) + random.random()
            moistAvg = random.randint(20,80) / 100
            moistBias = random.randint(5,10) / 100

            length = 48
            userActList = []
            tempList = []
            moistList = []
            lightList = []
            connList = []
            for i in range(length):
                transMat = [
                    [0.6, 0.3, 0, 0.1],
                    [0.2, 0.8, 0, 0],
                    [0, 0, 0, 0],
                    [0.6, 0.1, 0, 0.3]
                ]
                if(i <= 14):
                    state = 2
                elif(i >= 24 and i <= 2):
                    ran = random.random()
                    if(ran > 0.5):
                        state = 2
                    else:
                        state = 0
                else:
                    thres1 = transMat[state][0]
                    thres2 = thres1 + transMat[state][1]
                    if(state == 2):
                        state = 0
                    else:
                        ran = random.random()
                        if(ran <= thres1):
                            state = 0
                        elif(ran <= thres2):
                            state = 1
                        else:
                            state = 3
                userActList.append(state + 1)

                tempList.append(tempBias * math.sin(((i / 2 - 8) / 12) * math.pi) + tempAvg)
                
                moistList.append(moistBias * math.sin(((i / 2 + 4) / 12) * math.pi) + moistAvg)
                
                if(i > 14 and i < 34):
                    lightList.append(random.randint(60, 100))
                elif((i >= 10 and i <= 14) or (i >= 34 and i <= 38)):
                    lightList.append(random.randint(40, 80))
                else:
                    lightList.append(10)

                ran = random.random()
                if(ran > 0.99):
                    connList.append(0)
                else:
                    connList.append(1)
            data.append([userActList, tempList, moistList, lightList, connList])
    df = pd.DataFrame(data, columns=['userAct','temp','moist','light','conn'])
    df.to_csv(envfile)

def loadEnvfile():
    envfile = open('env.csv','r')
    df = pd.read_csv(envfile)
    for i in range(df.shape[0]):
        envdata.append(df.iloc[i])
    #useractlist = envdata[1]['userAct']
    #useractlist = useractlist[1:len(useractlist)-1].split(', ')
    #useractlist = [float(data) for data in useractlist]
    #print(useractlist)

def plotScatter():
    #print("U:" + str(avgU1))
    fig = plt.figure()          
    ax =fig.add_subplot(1,1,1)   
    x = np.arange(0,len(avgU1))
    y1 = np.array(avgU1)
    y2 = np.array(avgU2) 
    print("U1:" + str(y1))
    print("U2:" + str(y2))     
    print("\navgU1: " + str(np.mean(y1)) + " avgU2: " + str(np.mean(y2)))
    print("\nvarU1: " + str(np.std(y1)) + " varU2: " + str(np.std(y2)))
    ax.scatter(x,y1,s=20,c='y',alpha=0.5,lw=2,facecolors='none',label='1-layer')  
    ax.scatter(x,y2,s=20,c='r',alpha=0.5,lw=2,facecolors='none',label='2-layer')  
    ax.set_xticks((0,5,10,15,20))
    ax.legend()
    plt.show()  
    
    
if __name__ == '__main__':
    generateEnv(2)    
    loadEnvfile()
    #runexpBase()
    runexp1l()
    runexp2l()
    plotScatter()