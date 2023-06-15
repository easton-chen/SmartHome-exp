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

    def update(self, t):
        self.userAct = self.userActList[t]
        self.temp = self.tempList[t]
        self.moist = self.moistList[t]
        self.light = self.lightList[t]
        self.conn = self.connList[t]

    def predict(self, t):
        pass

    def show(self):
        print("userAct:" + str(self.userAct))
        print("temperature:" + str(self.temp))
        print("moisture:" + str(self.moist))
        print("lightning:" + str(self.light))
        print("connection:" + str(self.conn))

    def generate(self):
        length = 48
        tempAvg = 28
        tempBias = 5
        moistAvg = 0.4
        moistBias = 0.2
        for i in range(length):
            self.userActList.append(0)
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