import CGM
from Environment import env
import MPCController
import numpy as np 
import matplotlib.pyplot as plt


def runexp1():
    timeLimit = 48
    t = 0
    x_p = np.array([0, MPCController.Env.tempList[0], MPCController.Env.moistList[0], 0]).reshape(-1,1)
    
    cpList = []
    piList = []
    
    for i in range(timeLimit):
    # update environment

    # whether adapt mpc setting or not
    # mpcAdaptor.adapt(t, mpc)
    
    # mpc control 
        u0, x_p = MPCController.plan(x_p)
        cpList.append(u0)
        piList.append(x_p)
    # effect control to system
    
    
    x = np.arange(0,48)

    fig = plt.figure(num=1, figsize=(8, 8)) 
    ax1 = fig.add_subplot(4,1,1)
    ax2 = fig.add_subplot(4,1,2)
    ax3 = fig.add_subplot(4,1,3)
    ax5 = fig.add_subplot(4,1,4)

    y1 = np.array([row[5] for row in cpList])
    y2 = np.array(env.userActList)
    ax1.plot(x, y1, label='auto alarm')
    ax1.plot(x, y2, label='user activity', color='red')
    ax1.set_yticks((0,1,2,3)) 
    ax1.legend(loc=(1.03,0.75)) 

    y3 = np.array(env.tempList[:48])
    y4 = np.array([row[1] for row in piList])
    ax2.plot(x, y3, label='outside temp')
    ax2.plot(x, y4, label='temp')
    ax2.set_yticks((10,15,20,25,30,35))
    ax2.legend(loc=(1.03,0.75)) 

    plt.subplots_adjust(left=0.1, right=0.7, bottom=0.1, top=0.9)

    plt.show()
    
if __name__ == '__main__':
    runexp1()