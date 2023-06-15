import CGM
import Environment
import AHP

def analysis():
    pass

def WAdapt(context):
    CW = CGM.CW
    weightVectors = []
    for i in range(len(context)):
        if(context[i].name == 'temperature'):
            if(context[i].state > 28):
                key = str(context[i].name) + "_0"
            else:
                key = str(context[i].name) + "_1"
        else:
            key = str(context[i].name) + "_" + str(context[i].state)
        if(key in CW):
            mat = CW[key]
            ahp = AHP.AHP(mat)
            weightVectors.append(ahp.get_eig())
        
    weightVector = [0, 0, 0]
    for i in range(len(weightVectors)):
        for j in range(3):
            weightVector[j] += weightVectors[i][j]
    for j in range(3):
        weightVector[j] = weightVector[j] / len(weightVectors)
    print(weightVector)
    return weightVector

def QCAdapt(context):
    W = CGM.W
    minSG = W.index(min(W))
    if(minSG == 0):
        CGM.budgetThreshold += 20
    elif(minSG == 1):
        CGM.budgetThreshold -= 20
    else:
        CGM.tempL -= 2
        CGM.tempU += 2
        CGM.moistL -= 0.1
        CGM.moistU += 0.1

def run():
    CGM.W = WAdapt(Environment.context)
    #QCAdapt()

if __name__ == '__main__':
    run()