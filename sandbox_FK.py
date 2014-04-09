# -*- coding: utf-8 -*-


import cPickle, datetime
import numpy as np
import pylab, math
from sklearn import linear_model
from sklearn import cross_validation
from sidekick_TK import *
import matplotlib.pyplot  as plt

##on crée la base et les tests


projects, statuses = load_data('sidekick')
list_share_test=[0.1,0.2,0.3,0.4,0.5]
dates = [10*i - 1 for i in range(1,101)]
dic_fig = {"figsize" :(15,15)}
fig,ax = plt.subplots(nrows=1, ncols=1, **dic_fig)
ax.set_title('Accuracy of logistic predictors (TEST)')
ax.set_xlabel('time')
ax.set_ylabel('accuracy')
ax.grid(True)
ax.set_xticks(np.arange(0,1000,100))
ax.set_yticks(np.arange(0.5,1.05,0.05))

def create_plot(share):
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(statuses, projects[:,2], test_size=share, random_state=0)
    accuracies_test = []
    accuracies_test_l_ = []
    for date in dates:
        X_test_fixed = X_test[:,date,1]
        X_train_fixed = X_train[:,date,1]
        accuracies_test_l_.append(SD.accuracy(SD.double_logit_predict(X_train_fixed,y_train,X_test_fixed),y_test))
        #accuracies_test_l.append(SD.accuracy(SD.simple_logit_predict(X_train_fixed,y_train,X_test_fixed),y_test))
        accuracies_test.append(SD.accuracy(SD.naive_predict(X_test_fixed),y_test))
        #accuracies_train_l_.append(SD.accuracy(SD.double_logit_predict(X_train_fixed,y_train,X_train_fixed),y_train))
        #accuracies_train_l.append(SD.accuracy(SD.simple_logit_predict(X_train_fixed,y_train,X_train_fixed),y_train))
        #accuracies_train.append(SD.accuracy(SD.naive_predict(X_train_fixed),y_train))
    dic_plot1= {"markeredgecolor":str(share) , "marker":"-"}
    ax.plot(dates,accuracies_test, label = 'benchmark (TEST)'+str(share),  **dic_plot1)
    dic_plot2= {"markeredgecolor":str(share) , "marker":":"}
    ax.plot(dates,accuracies_test_l_, label = 'double logistic (TEST)'+str(share), **dic_plot2)
    #ax.plot(dates,accuracies_test_l_, 'r-',label = 'logistic with zooms (TEST)')
    #ax.plot(dates,accuracies_train, 'k:', label = 'benchmark (TRAIN)')
    #ax.plot(dates,accuracies_train_l,'b:', label = 'simple logistic (TRAIN)')
    #ax.plot(dates,accuracies_train_l_, 'r:', label = 'logistic with zooms (TRAIN)')
    #pylab.plot(dates,accuracies_l__)

for share in list_share_test:
    create_plot(share)
fig.savefig('logistic-train-test.png')


