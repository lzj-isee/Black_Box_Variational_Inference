import numpy as np
import torch
from  torch.utils.data.dataloader import DataLoader
from torchvision import transforms
from data_load import DatasetFromCSV
from functions import*
import os
'''
Accelerated bbvi
'''
num_epochs=15
batchSize=256
S=20
dim=28*28+1
k=0.005
w=1
c=0.1
sizeA=10
#读取数据
transform=transforms.ToTensor()
train_data=DatasetFromCSV('./train_images_csv.csv','./train_labels_csv.csv',transforms=transform)
test_data=DatasetFromCSV('./test_images_csv.csv','./test_labels_csv.csv',transforms=transform)
train_loader=DataLoader(train_data,batch_size=batchSize,shuffle=True)

#定义变量，前28*28是权重w，最后一个是偏差项bias
mu_s=torch.zeros(dim,requires_grad=True)
log_sigma2_s=torch.zeros(dim,requires_grad=True)

#需要储存结果
elbo_list=[]
variance_list=[]
accuracy_list=[]

#AdaGrad
#G=torch.zeros((dim*2,dim*2))
G2=0
grad_last=None


#开始迭代
for epoch in range(num_epochs):
    for i ,data in enumerate(train_loader):
        images,labels=data_preprocess(data)
        M=len(train_loader)
        #过程变量
        gradient=torch.zeros((dim*2,S))
        elbo=torch.zeros(S)
        mu1=np.zeros(S)
        #1
        if(epoch==0 and i==0):
            for s in range(S):
                z_sample=sampleZ(mu_s,log_sigma2_s,dim)
                with torch.no_grad():
                    log_p=log_P(images,labels,z_sample,dim,M)
                log_q=log_Q(mu_s,log_sigma2_s,z_sample,M)
                log_q.backward()
                with torch.no_grad():
                    elbo[s]=log_p-log_q
                    gradient[0:dim,s]=mu_s.grad*elbo[s]*M
                    gradient[dim:,s]=log_sigma2_s.grad*elbo[s]*M
                    mu1[s]=gradient[0,s].item()
                mu_s.grad.data.zero_()
                log_sigma2_s.grad.data.zero_()
            with torch.no_grad():
                grad_last=gradient.mean(1)
                G2=torch.pow(grad_last.norm(),2)
        #3
        rho=k/(w+G2)**(1/3)
        #4
        mu_s_t=mu_s.clone().detach()
        log_sigma2_s_t=log_sigma2_s.clone().detach()
        mu_s.data+=rho*grad_last[0:dim]
        log_sigma2_s.data+=rho*grad_last[dim:]
        #5
        b=c*rho*rho
        #6
        for s in range(S):
            z_sample=sampleZ(mu_s,log_sigma2_s,dim)
            with torch.no_grad():
                log_p=log_P(images,labels,z_sample,dim,M)
            log_q=log_Q(mu_s,log_sigma2_s,z_sample,M)
            log_q.backward()
            with torch.no_grad():
                elbo[s]=log_p-log_q
                gradient[0:dim,s]=mu_s.grad*elbo[s]*M
                gradient[dim:,s]=log_sigma2_s.grad*elbo[s]*M
            mu_s.grad.data.zero_()
            log_sigma2_s.grad.data.zero_()
        with torch.no_grad():
            grad=gradient.mean(1)
            G2+=torch.pow(grad.norm(),2)
        #7
        detla=Delta(images,labels,M,mu_s,log_sigma2_s,mu_s_t,log_sigma2_s_t,S,sizeA,dim)
        grad_last=(1-b)*(grad_last+detla)+b*grad

        elbo_list.append(np.mean(elbo.detach().numpy()))#求elbo的均值加入list
        accuracy_list.append(accuracyCalc(mu_s,log_sigma2_s,test_data,dim))#在测试集上计算accuracy
        if (i+1)%10==0 or i<=10 and epoch==0:
            print('Epoch[{}/{}], step[{}/{}]'.format(\
                epoch+1,
                num_epochs,
                i+1,len(train_loader)))
            print('ELBO: {:.3f}, acc: {:.3f}\n'.format(\
                elbo_list[len(elbo_list)-1],
                accuracy_list[len(accuracy_list)-1]))
                #variance_list[len(variance_list)-1]))
        
if not os.path.exists('./result'):
    os.makedirs('./result')
result=np.array([elbo_list,variance_list,accuracy_list])
np.save('./result/bbvi_acc.npy',result)
