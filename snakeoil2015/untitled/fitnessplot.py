import matplotlib.pyplot as plt
import logs as log
import numpy as np


#DA evaluation_0_1 a evaluation_0_3015
id = 1
list1 = []
fit = []


i = 0
for j in range(1,3016):
    app = 'evaluation_'+i.__str__()+'_'+j.__str__()
    list1.append(getattr(log, app))

for elem in list1:
    fit.append(elem['fitness'])


mean = []
index = 0
var = []
var1 = []
var2 = []
k = 0


while index<3015:
    print (fit[index:index+15])
    mean.append(sum(fit[index:index+15])/15)
    var.append(np.var(fit[index:index+15]))
    var1.append(mean[k] + var[k])
    var2.append(mean[k] - var[k])
    k = k+1
    index = index+15


print('var1' , var1)
print("vettore delle medie", mean)
print('var2', var2)


epoch = range(len(mean))

plt.plot(epoch,var1)
plt.plot(epoch,mean)
plt.plot(epoch,var2)
plt.xlabel('Epochs')
plt.ylabel('Mean Fitness')
plt.show()



#DA evaluation_1_1 a evaluation_1_3015
'''id = 1
list1 = []
fit = []


i = 1
for j in range(1,3016):
    app = 'evaluation_'+i.__str__()+'_'+j.__str__()
    list1.append(getattr(log, app))

for elem in list1:
    fit.append(elem['fitness'])


mean = []
index = 0
var = []
var1 = []
var2 = []
k = 0


while index<3015:
    mean.append(sum(fit[index:index+15])/15)
    var.append(np.var(fit[index:index+15]))
    var1.append(mean[k] + var[k])
    var2.append(mean[k] - var[k])
    k = k+1
    index = index+15


print('var1' , var1)
print("vettore delle medie", mean)
print('var2', var2)


epoch = range(len(mean))

p = plt.plot(epoch,var1)
plt.plot(epoch,mean)
plt.plot(epoch,var2)
plt.xlabel('Epochs')
plt.ylabel('Mean Fitness')
plt.show()'''



