import CGM
import AHP

class MPCAdaptor:
    def __init__(self, Env):
        self.Env = Env


    def WAdapt(self, userAct, temp):
        CW = CGM.CW
        weightVectors = []
            
        if(temp > 28):
            key = "climate_0"
        else:
            key = "climate_1"
        if(key in CW):
            mat = CW[key]
            ahp = AHP.AHP(mat)
            weightVectors.append(ahp.get_eig())

        key = 'userAct_' + str(userAct)
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

    def adapt(self, t):
        userAct = self.Env.userActList[t]
        temp = self.Env.tempList[t]
        conn = self.Env.connList[t]
        
        weights = [0, 0, 0, 0]
        x_4_r = 100
        u_1_upper = 3
        u_6_lower = 0

        # weights WAdapt(userAct, temps)
        SGWeights = self.WAdapt(userAct, temp)
        weights = [SGWeights[0], SGWeights[2]/2, SGWeights[2]/2, SGWeights[1]]
        # reference value sleep->light
        if(userAct == 2):
            x_4_r = 0

        # constraints conn->ac, useract->al
        if(conn == 0):
            u_1_upper = 0
        if(userAct == 3):
            u_6_lower = 1
        
        
        return weights, x_4_r, u_1_upper, u_6_lower