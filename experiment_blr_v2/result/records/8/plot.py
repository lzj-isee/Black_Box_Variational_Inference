import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

bbvi_basic=np.load('./result/records/8/bbvi_basic.npy')
abbvi_basic=np.load('./result/records/8/abbvi_basic.npy')
bbvi_cv=np.load('./result/records/8/bbvi_cv.npy')
abbvi_cv=np.load('./result/records/8/abbvi_cv.npy')

x=np.array(range(len(bbvi_basic)))


plt.plot(x,abbvi_cv,label='abbvi_cv',alpha=0.8)
plt.plot(x,bbvi_cv,label='bbvi_cv',alpha=0.8)
#plt.plot(x,abbvi_basic,label='abbvi_basic',alpha=0.8)
#plt.plot(x,bbvi_basic,label='bbvi_basic',alpha=0.8)


plt.legend()
plt.grid()
plt.show()

'''
# setting:  
## both  
num_epochs=15  
batchSize=120  
num_St=2000  

  
## bbvi & bbvi_cv  
num_S=5#训练的采样数量  
eta=0.3
  

# abbvi  
num_S=5#训练的采样数量  
eta=0.05  
k=0.4  
w=1  
c=5e6 -> b=1~0.226  
M=10  


# abbvi_cv  
num_S=5  
k=0.4  
w=1  
c=5.5e6 -> b=1~0.38  
M=10  

PS: abbvi_cv的b虽然不小，但是已经很极限
'''
