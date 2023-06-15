import numpy as np
class AHP:
    
    def __init__(self,array):
        self.array = array
        # matrix shape
        self.n = array.shape[0]
        # initial RI value for consistent test 
        RI_list = [0,0,0.58,0.90,1.12,1.24,1.32,1.41,1.45]
        self.RI = RI_list[self.n-1]
        
	#获取最大特征值和对应的特征向量
    def get_eig(self):
        #numpy.linalg.eig() 计算矩阵特征值与特征向量
        eig_val ,eig_vector = np.linalg.eig(self.array)
        #获取最大特征值
        max_val = np.max(eig_val)
        max_val = round(max_val.real, 4)
        #通过位置来确定最大特征值对应的特征向量
        index = np.argmax(eig_val)
        max_vector = eig_vector[:,index]
        max_vector = max_vector.real.round(4) 
        #添加最大特征值属性
        self.max_val = max_val
        #计算权重向量W
        weight_vector = max_vector/sum(max_vector)
        weight_vector = weight_vector.round(4)
        #打印结果
        #print("最大的特征值: "+str(max_val))
        #print("对应的特征向量为: "+str(max_vector))
        #print("归一化后得到权重向量: "+str(weight_vector))
        return weight_vector
    
    
    def test_consitst(self):
        #calculate CI 
        CI = (self.max_val-self.n)/(self.n-1) 
        CI = round(CI,4) 
        
        print("判断矩阵的CI值为" +str(CI))
        print("判断矩阵的RI值为" +str(self.RI))
       
        if self.n == 2:
            print("only two factor, no problem")
        else:
            #计算CR值
            CR = CI/self.RI 
            CR = round(CR,4)
            #CR < 0.10 pass
            if  CR < 0.10 :
                print("判断矩阵的CR值为" +str(CR) + "，通过一致性检验")
                return True
            else:
                print("判断矩阵的CR值为" +str(CR) + "，未通过一致性检验")
                return False

if __name__ == "__main__": 
    mat = np.array([[1,10,10],[0.1,1,1],[0.1,1,1]])
    print(mat)
    ahp = AHP(mat)
    ahp.get_eig()
    ahp.test_consitst()