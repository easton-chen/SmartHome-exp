import CGM
import Environment_old
import ConController
import ReqController
import matplotlib.pyplot as plt
import numpy as np



context = Environment_old.context
def environmentUpdate(time):
    
    for i in range(len(context)):
        context[i].update(time)
    

# statictis
# context
userActdata = []
tempdata = []
moistdata = []
lightdata = []
networkdata = []
# utility
utilitydata = []
noadaptutilitydata = []
# weight
weightdata0 = []
weightdata1 = []
weightdata2 = []
# CP
autoalarmdata = []
fandata = []
airconddata = []

def showStat():
    CP = CGM.CP
    PICost = CGM.calPICost(CP.airCond, CP.humidifier, CP.autoAlarm, CP.light, CP.fans)
    PILight = CGM.calPILight(CP.light, CP.curtain)
    PITemp = CGM.calPITemp(CP.airCond, CP.fans)
    PIMoist = CGM.calPIMoist(CP.humidifier)
    
    SGBudget = CGM.SGBudgetQC(PICost)
    SGLight = CGM.SGLightQC(PILight)
    SGComfort = CGM.SGComfortQC(PITemp, PIMoist)

    utility = CGM.W[0] * SGBudget + CGM.W[1] * SGLight + CGM.W[2] * SGComfort

    print("Control Parameter:")
    print("airCond: " + str(CP.airCond) + " humidifier: " + str(CP.humidifier) + " autoAlarm: " + str(CP.autoAlarm)
          + " light: " + str(CP.light) + " curtain: " + str(CP.curtain))
    
    print("Performance Indicator:")
    print("Cost: " + str(PICost) + " Light: " + str(PILight) + " Temp: " + str(PITemp) + " Moist: " + str(PIMoist))

    print("Softgoal:")
    print("weights: " + str(CGM.W))
    print("Budget: " + str(SGBudget) + " Light: " + str(SGLight) + " Comfort: " + str(SGComfort))
    print("Softgoal Utility: " + str(utility))

    # collect data
    userActdata.append(Environment_old.userAct.state)
    tempdata.append(Environment_old.temperature.state)
    moistdata.append(Environment_old.moisture.state)
    lightdata.append(Environment_old.lighting.state)
    networkdata.append(Environment_old.network.state)
    

    utilitydata.append(utility)
    

    weightdata0.append(CGM.W[0])
    weightdata1.append(CGM.W[1])
    weightdata2.append(CGM.W[2])
    

    autoalarmdata.append(CP.autoAlarm)
    if(CP.airCond < 16):
        airconddata.append(0)
    else:
        airconddata.append(1)
    fandata.append(CP.fans)
    
   
    return SGBudget, SGLight, SGComfort

def runexp1():
    simloop = 24
    time = 0
    for i in range(simloop):
        environmentUpdate(time)
        print("\nCurrent time: " + str(time))
        print("Context:")
        Environment_old.showContext()
        
        curUtility = -1 * ConController.utilityFun([CGM.CP.airCond, CGM.CP.humidifier, CGM.CP.autoAlarm, CGM.CP.light, CGM.CP.curtain, CGM.CP.fans])
        noadaptutilitydata.append(curUtility)

        ReqController.run()   
        ConController.run()  
        showStat()

        time = (time + 1) % 24

    np.save("userActdata.npy", userActdata)
    np.save("tempdata.npy", tempdata)
    np.save("moistdata.npy", moistdata)
    np.save("lightdata.npy", lightdata)
    np.save("networkdata.npy", networkdata)
    np.save("utilitydata.npy",utilitydata)
    np.save("weightdata0.npy",weightdata0)
    np.save("weightdata1.npy",weightdata1)
    np.save("weightdata2.npy",weightdata2)
    np.save("autoalarmdata.npy",autoalarmdata)
    np.save("airconddata.npy",airconddata)
    np.save("fandata.npy",fandata)

    np.save("noadaptutilitydata.npy",noadaptutilitydata)

def plot1all():
    x = np.arange(0,24)

    y1 = np.load("autoalarmdata.npy")
    y2 = np.load("userActdata.npy")
    y3 = np.load("utilitydata.npy")
    y4 = np.load("weightdata0.npy")
    y5 = np.load("weightdata1.npy")
    y6 = np.load("weightdata2.npy")
    y7 = np.load("networkdata.npy")
    y8 = np.load("airconddata.npy")
    y9 = np.load("fandata.npy")
    y10 = np.load("noadaptutilitydata.npy")

    fig = plt.figure(num=1, figsize=(8, 8)) 
    ax1 = fig.add_subplot(4,1,1)
    ax2 = fig.add_subplot(4,1,2)
    ax3 = fig.add_subplot(4,1,3)
    ax5 = fig.add_subplot(4,1,4)

    ax1.plot(x, y1, label='auto alarm')
    ax1.plot(x, y2, label='user activity', color='red')
    ax1.set_yticks((0,1,2,3)) 
    ax1.legend(loc=(1.03,0.75)) 
    

    ax2.plot(x, y3, label='utility')
    ax2.plot(x, y10, label='utility wo adaptation', linestyle=':')
    ax2.set_yticks((0,0.2,0.4,0.6,0.8,1))
    ax2.legend(loc=(1.03,0.75)) 
    

    #ax3.plot(x, y2, label='user activity')
    ax3.plot(x, y4, label='budget weight', linestyle=':')
    ax3.plot(x, y5, label='lighting weight', linestyle=':')
    ax3.plot(x, y6, label='body comfort weight', linestyle=':')
    ax3.set_yticks((0,0.2,0.4,0.6,0.8))
    ax3.legend(loc=(1.04,0.5)) 
    ax3.spines['right'].set_visible(False)
    ax4 = ax3.twinx()
    ax4.plot(x, y2, color='red', label='user activity')
    ax4.set_yticks((0, 1, 2, 3))
    ax4.legend(loc=(1.04,0.25))

    ax5.plot(x, y7, label='network')
    ax5.plot(x, y8, label='air-conditioner')
    ax5.plot(x, y9, label='fans')
    ax5.legend(loc=(1.03,0.5))
    ax5.set_xlabel('time') 
    plt.subplots_adjust(left=0.1, right=0.7, bottom=0.1, top=0.9)

    plt.show()

def plot1():
    x = np.arange(0,24)
    y1 = np.load("./exp1data/autoalarmdata.npy")
    y2 = np.load("./exp1data/userActdata.npy")
    y3 = np.load("./exp1data/utilitydata.npy")
    y4 = np.load("./exp1data/weightdata0.npy")
    y5 = np.load("./exp1data/weightdata1.npy")
    y6 = np.load("./exp1data/weightdata2.npy")
    y7 = np.load("./exp1data/networkdata.npy")
    y8 = np.load("./exp1data/airconddata.npy")
    y9 = np.load("./exp1data/fandata.npy")
    y10 = np.load("./exp1data/noadaptutilitydata.npy")

    # user activity -- auto alarm
    fig1 = plt.figure(num=1, figsize=(8, 3)) 
    ax1 = fig1.add_subplot(1,1,1)

    ax1.plot(x, y1, label='auto alarm',marker='*')
    ax1.plot(x, y2, label='user activity', color='red',marker='.')
    ax1.set_yticks((0,1,2,3)) 
    ax1.xaxis.set_label_coords(1.05, -0.03)
    ax1.xaxis.set_label_position('bottom')
    ax1.set_xlabel('time')
    #ax1.legend(loc=(1.03,0.75)) 
    ax1.legend(loc='best')
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
    plt.show()

    # utility
    fig2 = plt.figure(num=2, figsize=(8, 3)) 
    ax2 = fig2.add_subplot(1,1,1)
    
    ax2.plot(x, y3, label='utility',marker='*')
    ax2.plot(x, y10, label='utility wo adaptation', linestyle=':',marker='*')
    ax2.set_xlabel('time')
    ax2.xaxis.set_label_coords(1.05, -0.03)
    ax2.xaxis.set_label_position('bottom')
    ax2.set_yticks((0,0.2,0.4,0.6,0.8,1))
    #ax2.legend(loc=(1.03,0.75)) 
    ax2.legend(loc='best')
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
    plt.show()
    
    # user activity -- weights
    fig3 = plt.figure(num=3, figsize=(8, 3)) 
    ax3 = fig3.add_subplot(1,1,1)

    ax3.plot(x, y4, label='budget weight', linestyle=':',marker='*')
    ax3.plot(x, y5, label='lighting weight', linestyle=':',marker='*')
    ax3.plot(x, y6, label='body comfort weight', linestyle=':',marker='*')
    ax3.set_yticks((0,0.2,0.4,0.6,0.8))
    #ax3.legend(loc=(1.04,0.7)) 
    ax3.legend(loc='best')
    ax3.spines['right'].set_visible(False)
    ax4 = ax3.twinx()
    ax4.plot(x, y2, color='red', label='user activity',marker='.')
    ax3.set_xlabel('time')
    ax3.xaxis.set_label_coords(1.05, -0.03)
    ax3.xaxis.set_label_position('bottom')
    ax4.set_yticks((0, 1, 2, 3))
    #ax4.legend(loc=(1.04,0.45))
    ax4.legend(loc='best')
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
    plt.show()
    
    fig4 = plt.figure(num=4, figsize=(8, 3)) 
    ax5 = fig4.add_subplot(1,1,1)
    ax5.plot(x, y7, label='network',color='red',marker='.')
    ax5.plot(x, y8, label='air-conditioner',marker='*', linestyle=':')
    ax5.plot(x, y9, label='fans',marker='*', linestyle=':')
    #ax5.legend(loc=(1.03,0.7))
    ax5.legend(loc='best')
    ax5.set_xlabel('time') 
    ax5.xaxis.set_label_coords(1.05, -0.03)
    ax5.xaxis.set_label_position('bottom')
    ax5.set_yticks((0,1))
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
    plt.show()

def runexp2():
    avgU1 = []
    avgU2 = []
    for i in range(30):
        # old context
        Environment_old.randomContext()
        Environment_old.userAct.state = 1
        #Environment.temperature.state = 20
        print("old context")
        Environment_old.showContext()

        Environment_old.userAct.state = 0 
        #Environment.temperature.state = 10
        print("new context")
        Environment_old.showContext()
        # 
        CGM.W = [0.33,0.33,0.33]


        # 1 layer
        ConController.run()
        print("\n1 layer")
        SGBudget1, SGLight1, SGComfort1 = showStat()
        #baseUtility = W_[0] * SGBudget + W_[1] * SGLight + W_[2] * SGComfort
        #print("\nbaseline utility for 1:" + str(baseUtility))

        # 2 layer
        ReqController.run()
        ConController.run()
        print("\n2 layer")
        SGBudget2, SGLight2, SGComfort2 = showStat()
        W = CGM.W
        Utility1 = W[0] * SGBudget1 + W[1] * SGLight1 + W[2] * SGComfort1
        Utility2 = W[0] * SGBudget2 + W[1] * SGLight2 + W[2] * SGComfort2
        avgU1.append(Utility1)
        avgU2.append(Utility2)
        print("\nutility for 1:" + str(Utility1) + "\nutility for 2:" + str(Utility2))
    

    fig = plt.figure()          
    ax =fig.add_subplot(1,1,1)   
    x = np.arange(0,30)
    y1 = np.array(avgU1)
    y2 = np.array(avgU2)      
    print("\navgU1: " + str(np.mean(y1)) + " avgU2: " + str(np.mean(y2)))
    print("\nvarU1: " + str(np.std(y1)) + " varU2: " + str(np.std(y2)))
    ax.scatter(x,y1,s=20,c='y',alpha=0.5,lw=2,facecolors='none',label='single layer')  
    ax.scatter(x,y2,s=20,c='r',alpha=0.5,lw=2,facecolors='none',label='two layer')  
    ax.legend()
    plt.show()  

if __name__ == '__main__':
    runexp1()
    plot1all()
    #plot1()