import cPickle, datetime
import numpy as np
import scikitlearn, pylab, math
from sklearn import linear_model

def load_binary(file_name):
    with open(file_name, 'rb') as f:
        return cPickle.load(f)


def load_data(dir_name):
    print 'Loading projects...'
    projects = np.load(dir_name + '/projects.npy')
    print 'Loading statuses...'
    statuses = load_binary(dir_name +'/statuses.pkl')
#    print 'Loading tweets...'
#    tweets = np.load('%s/tweets.npy' % (args.data_dir, ))
#    print 'Loading graph...'
#    graph = np.load('%s/graph.pkl' % (args.data_dir, ))
    # conver to numpy arrays if needed
    statuses = np.array(statuses)
    return projects, statuses#, tweets, graph


def print_project(num_project):
    project = projects[num_project]
    project_statuses = statuses[num_project]
    print 'Project number: ' + str(num_project)
    print 'Id: ' + str(project[0])
    print 'Goal: ' + str(project[1])
    print 'State: ' + 'successful' if project[2] == 1 else 'failed'
    print 'Launch: ' +  str(project[3]) # unix timestamp
    print 'Deadline: ' + str(project[4]) # unix timestamp
    return project, project_statuses


def print_status(num_project,num_status):
    status = statuses[num_project,num_status]
    project = projects[num_project]
    print str(num_status) + 'th status of the ' + str(num_project) + 'th project'
    print 'Time: ' + str(status[0])
    print 'True time: ' + str(status[0] * (project[4] - project[3]) + project[3])
    print 'Pledged money: ' + str(status[1])
    print 'Number of backers: ' + str(status[2])


def accuracy(predictions,Y):
    n = len(predictions)
    right = 0
    if n != len(Y): 
        print "error: length don't match"
    for i in range(n):
        right += predictions[i]==float(Y[i])
    return float(right)/n

### Benchmark with naive predictor

projects, statuses = load_data('sidekick')

def  naive_predict(X):
    return [float(x>=1) for x in X]

accuracies = []
dates = [10*i - 1 for i in range(1,101)]
for date in dates:
    X1 = statuses[:,date,1]
    accuracies.append(accuracy(naive_predict(X1),Y))

pylab.plot(dates,accuracies)
pylab.title('Benchmark: accuracy (naive predictor)')
pylab.xlabel('time')
pylab.ylabel('accuracy of naive predictor')
pylab.grid(True)
pylab.savefig('benchmark.png')
pylab.show()




### Simple logistic predictor

dates = [10*i - 1 for i in range(1,101)]

def simple_logit_predict(X,Y):
    XX = X[:,np.newaxis]
    lr = linear_model.LogisticRegression()
    lr.fit(XX,Y)
    return lr.predict(XX)


accuracies_l = []
for date in dates:
    X1 = statuses[:,date,1]
    accuracies_l.append(accuracy(simple_logit_predict(X1,Y),Y))


### Variations around the simple predictor

### Testing for fitting logistic with additionnal 1/X-like variable
def double_logit_predict(X,Y):
    X_1 = np.empty_like(X)
    X_2 = np.empty_like(X)    
    for i in range(len(X)): 
        X_1[i] = (X[i]+0.05)**(-1)
        X_2[i] = 100 if 1.0 - X[i] < 0.01 else (1.0 - X[i])**(-1)
    XX = np.vstack((X,X_1,X_2)).T
    lr = linear_model.LogisticRegression()
    lr.fit(XX,Y)
    return lr.predict(XX)
### Observations: additionnal 1/X-like variable provides a significant improvement especially for the early stages


accuracies_l_ = []
for date in dates:
    X = statuses[:,date,1]
    accuracies_l_.append(accuracy(double_logit_predict(X,Y),Y))

### Testing for fitting logistic to non-yet-successful campaigns
accuracies_l_ = []
accuracies_l__ = []
for date in dates:
    X = statuses[:,date,1]
    lX = []
    lY = []
    for i in range(len(X)): 
        if X[i] < 1.0: #Excluding already successful campaigns
            lX.append(X[i])
            lY.append(Y[i])
    XX = np.array(lX)
    YY = np.array(lY)
    p = float(len(XX))/len(X) #Ratio of non-yet-successful campaigns
#    accuracies_l_.append(1.0-p + p*accuracy(simple_logit_predict(XX,YY),YY))#Adjusting accuracy
    accuracies_l__.append(1.0-p + p*accuracy(double_logit_predict(XX,YY),YY))#Adjusting accuracy
### Observations: fitting to non-yet-successful campaigns does not provide significant improvements for accuracy


pylab.plot(dates,accuracies)
pylab.plot(dates,accuracies_l)
pylab.plot(dates,accuracies_l_)
#pylab.plot(dates,accuracies_l__)
pylab.title('Accuracy of simple logistic predictor')
pylab.xlabel('time')
pylab.ylabel('accuracy of logistic predictor')
pylab.grid(True)
pylab.xticks(np.arange(0,1000,100))
pylab.yticks(np.arange(0.5,1.05,0.05))
pylab.savefig('logistic-1.png')
pylab.show()


alpha = []
alpha_1 = []
alpha_2 = []
dates = [10*i - 1 for i in range(1,101)]
for date in dates:
    X = statuses[:,date,1]
    X_1 = np.empty_like(X)
    X_2 = np.empty_like(X)
    for i in range(len(X)): 
        X_1[i] = (X[i] + 0.01)**(-1)
        X_2[i] = 100 if 1.0 - X[i] < 0.01 else (1.0 - X[i])**(-1)
    XX = np.vstack((X,X_1,X_2)).T
    Y = projects[:,2]
    lr = linear_model.LogisticRegression(C=10)
    lr.fit(XX,Y)
    alpha.append(lr.coef_[0][0])
    alpha_1.append(lr.coef_[0][1])
    alpha_2.append(lr.coef_[0][2])


pylab.plot(dates,alpha_1)
pylab.show()
### Observations:   - pretty stable
#                   - magnitude 


