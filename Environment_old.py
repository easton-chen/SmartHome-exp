import random
import math

class UserAct:
    # [normal, work, sleep, none]
    def __init__(self, name):
        self.name = name
        self.state = 0
        self.transMat = [
            [0.6, 0.3, 0, 0.1],
            [0.2, 0.8, 0, 0],
            [0, 0, 0, 0],
            [0.6, 0.1, 0, 0.3]
        ]

    def update(self,t):
        if(t <= 7):
            self.state = 2
        elif(t >= 12 and t <= 13):
            ran = random.random()
            if(ran > 0.5):
                self.state = 2
            else:
                self.state = 0
        else:
            thres1 = self.transMat[self.state][0]
            thres2 = thres1 + self.transMat[self.state][1]
            if(self.state == 2):
                self.state = 0
            else:
                ran = random.random()
                if(ran <= thres1):
                    self.state = 0
                elif(ran <= thres2):
                    self.state = 1
                else:
                    self.state = 3
        #self.state = random.randint(0, 3)

class Temperature:
    def __init__(self, name, avg, bias):
        self.name = name
        self.state = avg
        self.avg = avg
        self.bias = bias

    def update(self,t):
        self.state = self.bias * math.sin(((t - 8) / 12) * math.pi) + self.avg

class Network:
    def __init__(self, name):
        self.name = name
        self.state = 1

    def update(self,t):
        ran = random.random()
        if(ran > 0.99):
            self.state = 0
        else:
            self.state = 1
        if(t == 13):
            self.state = 0

class Time:
    def __init__(self, name):
        self.name = name
        self.state = 0

    def update(self,t):
        self.state = t

class Moisture:
    def __init__(self, name, avg, bias):
        self.name = name
        self.state = avg
        self.avg = avg
        self.bias = bias

    def update(self,t):
        self.state = self.bias * math.sin(((t + 4) / 12) * math.pi) + self.avg

class Lighting:
    def __init__(self, name):
        self.name = name
        self.state = 0

    def update(self,t):
        if(t >= 6 and t <= 18):
            self.state = random.randint(60, 100)
        else:
            self.state = 10

class Noise:
    def __init__(self, name):
        self.name = name
        self.state = 0

    def update(self,t):
        if(t <= 6):
            self.state = 20
        else:
            self.state = random.randint(20, 60)


userAct = UserAct("userAct")
temperature = Temperature("temperature", 24, 6)
network = Network("network")
time = Time("time")
moisture = Moisture("moisture", 0.5, 0.2)
lighting = Lighting("lighting")
#noise = Noise("noise")
context = []
context.append(userAct)
context.append(temperature)
context.append(network)
context.append(time)
context.append(moisture)
context.append(lighting)
#context.append(noise)

def randomContext():
    userAct.state = random.randint(0,3)
    temperature.state = random.randint(10,35) + random.random()
    time.state = random.randint(0,23)
    moisture.state = random.random()
    lighting.update(time.state)
    network.update(0)

def showContext():
    cv = ""
    for i in range(len(context)):
        cv += str(context[i].name) + ": " + str(context[i].state) + " "
    print(cv + '\n')

def envPredict(t):
    pass