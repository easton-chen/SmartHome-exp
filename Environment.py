import random
import math

class Environment:
    def __init__(self):
        self.userAct = 0
        self.temp = 0
        self.moist = 0
        self.light = 0
        self.conn = 0
        self.userActList = []
        self.tempList = []
        self.moistList = []
        self.lightList = []
        self.connList = []
        self.oldcnt = [0, 0, 0]
        self.cnt = [0, 0, 0]

    def update(self, t):
        self.userAct = self.userActList[t]
        self.temp = self.tempList[t]
        self.moist = self.moistList[t]
        self.light = self.lightList[t]
        self.conn = self.connList[t]
        for i in range(len(self.cnt)):
            self.oldcnt[i] = self.cnt[i]
        self.contextOp()

    def predict(self, t):
        pass

    def show(self):
        print("userAct:" + str(self.userAct))
        print("temperature:" + str(self.temp))
        print("moisture:" + str(self.moist))
        print("lightning:" + str(self.light))
        print("connection:" + str(self.conn))
        print("context:" + str(self.cnt))

    def generate(self):
        case = 1
        print("generate random environment " + str(case))
        
        if(case == 0):
            # no meta adapt
            length = 48
            tempAvg = 28
            tempBias = 6
            moistAvg = 0.4
            moistBias = 0.25

            for i in range(length):
                self.userActList.append(1)

                self.tempList.append(tempBias * math.sin(((i / 2 - 8) / 12) * math.pi) + tempAvg)
                
                self.moistList.append(moistBias * math.sin(((i / 2 + 4) / 12) * math.pi) + moistAvg)
                
                if(i > 14 and i < 34):
                    self.lightList.append(random.randint(60, 100))
                elif((i >= 10 and i <= 14) or (i >= 34 and i <= 38)):
                    self.lightList.append(random.randint(40, 80))
                else:
                    self.lightList.append(10)

                self.connList.append(1)
                
            for i in range(3):
                self.lightList.append(self.lightList[47])
                self.tempList.append(self.tempList[47])
                self.moistList.append(self.moistList[47])



        elif(case == 1):
            length = 48
            tempAvg = 28
            tempBias = 5
            moistAvg = 0.4
            moistBias = 0.2
            
            for i in range(length):
                if(i < 15):
                    self.userActList.append(3)
                else:
                    self.userActList.append(2)

                self.tempList.append(tempBias * math.sin(((i / 2 - 8) / 12) * math.pi) + tempAvg)
                self.moistList.append(moistBias * math.sin(((i / 2 + 4) / 12) * math.pi) + moistAvg)
                if(i > 14 and i < 34):
                    self.lightList.append(random.randint(60, 100))
                elif((i >= 10 and i <= 14) or (i >= 34 and i <= 38)):
                    self.lightList.append(random.randint(40, 80))
                else:
                    self.lightList.append(10)

                ran = random.random()
                if(ran > 0.99):
                    self.connList.append(0)
                else:
                    self.connList.append(1)

            for i in range(3):
                self.lightList.append(self.lightList[47])
                self.tempList.append(self.tempList[47])
                self.moistList.append(self.moistList[47])

        
        self.userAct = self.userActList[0]
        self.temp = self.tempList[0]
        self.moist = self.moistList[0]
        self.light = self.lightList[0]
        self.conn = self.connList[0]
        self.contextOp()
    
    def contextOp(self):
        # c1(idle): userAct = 1; c2(work): userAct = 2; c3(sleep):userAct = 3; c4(away): userAct = 4
        # c5(extrem): temp >= 28 or temp <= 10; c6(normal): temp < 28 and temp > 10
        # c7(network): conn = 1
        self.cnt[0] = self.userAct
        self.cnt[2] = self.conn
        if(self.temp >= 28 or self.temp <= 10):
            self.cnt[1] = 5
        else:
            self.cnt[1] = 6

    def cntChange(self):
        flag = False
        for i in range(len(self.cnt)):
            if(self.oldcnt[i] != self.cnt[i]):
                flag = True
        return flag
        

env = Environment()
env.generate()


