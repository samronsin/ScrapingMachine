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
    statuses = np.array(statuses)
    return projects, statuses#, tweets, graph


def load_tweets_data(dir_name):
    print 'Loading tweets...'
    tweets = np.load( dir_name + '/tweets.npy')
    return tweets


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


def print_tweets(num_project,num_tweet):
    tweet = tweets[num_project,num_tweet]
    project = projects[num_project]
    print str(num_tweet) + 'th sample of tweets of the ' + str(num_project) + 'th project:'
    print 'Time: ' + str(tweets[num_project, num_tweet, 0])
    print 'Number of tweets: ' + str(tweets[num_project, num_tweet, 1])
    print 'Number of replies: ' + str(tweets[num_project, num_tweet, 2])
    print 'Number of retweets: ' + str(tweets[num_project, num_tweet, 3])
    print 'Estimated number of backers: ' + str(tweets[num_project, num_tweet, 4])
    print 'Number of users who tweeted: ' + str(tweets[num_project, num_tweet, 5])


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

### Testing for fitting logistic with additionnal lag variable
def lag_logit_predict(XX,Y):
    lr = linear_model.LogisticRegression()
    lr.fit(XX,Y)
    return lr.predict(XX)


accuracies_l_ = []
for date in dates:
    X = statuses[:,date,1]
    #lag_date = date-100 if date >= 100 else 0
    X_1 = statuses[:,int(date*0.9),1]
    X_2 = statuses[:,int(date*0.8),1]
    X_3 = statuses[:,int(date*0.7),1]
    X_4 = statuses[:,int(date*0.6),1]
    X_5 = statuses[:,date/2,1]   
    XX = np.vstack((X,X_1,X_2,X_3,X_4,X_5)).T
    accuracies_l_.append(accuracy(lag_logit_predict(XX,Y),Y))
### Observations: lags don't provide significant explanatory power


### Testing for fitting logistic with additionnal dummies
def dummies_logit_predict(XX,Y):
    lr = linear_model.LogisticRegression()
    lr.fit(XX,Y)
    return lr.predict(XX)


money_lost = np.zeros_like(statuses[:,0,1])
is_success = np.zeros_like(statuses[:,0,1])


accuracies_l_ = []
for date in dates:
    X = statuses[:,date,1]
    date_lag = date - 10 if date >=10 else 0
    X_lag = statuses[:,date_lag,1]
    for j in range(len(money_lost)):
        money_lost[j] = money_lost[j] or (X[j] < X_lag[j])
        is_success[i] = float( X[j] >= 1.0 )
    XX = np.vstack((X,money_lost#,
        #is_success
        )).T
    accuracies_l_.append(accuracy(dummies_logit_predict(XX,Y),Y))
### Observation:   dummy on losing backers' money provides siginificant explanatory power
### Observation:   dummy on being already successful don't provide any explanatory power


### Testing for fitting logistic with tweets data


accuracies_l_t = []
for t in dates:
    X0 = statuses[:,t,1]
    Tw1 = tweets[:,t,1]#Tweets
    Tw2 = tweets[:,t,2]#Retweets
    Tw3 = tweets[:,t,3]#Replies
    Tw4 = tweets[:,t,4]#Estimation of number of backers
    Tw5 = tweets[:,t,5]#Users who tweeted
    XX = np.vstack((X0,
    Tw1,Tw2,Tw3,Tw4,Tw5
        )).T
    accuracies_l_t.append(accuracy(lag_logit_predict(XX,Y),Y))
### Observation:   dummy on losing backers' money provides siginificant explanatory power


pylab.plot(dates,accuracies, label = 'benchmark')
pylab.plot(dates,accuracies_l, label = 'simple logistic')
#pylab.plot(dates,accuracies_l_, label = 'logistic with zooms')
pylab.plot(dates,accuracies_l_t, label = 'logistic with tweets data')
#pylab.plot(dates,accuracies_l__)
pylab.title('Accuracy of logistic predictors')
pylab.xlabel('time')
pylab.ylabel('accuracy')
pylab.grid(True)
pylab.xticks(np.arange(0,1000,100))
pylab.yticks(np.arange(0.5,1.05,0.05))
pylab.legend(loc='lower center',fancybox=True)
pylab.savefig('logistic-4.png')
pylab.size(12)
pylab.show()


const = []
alpha = []
alpha_1 = []
alpha_2 = []
probas_simple = []
predict_simple = []
dates = [10*i - 1 for i in range(1,101)]
for date in dates:
    X = statuses[:,date,1]
    #X_1 = np.empty_like(X)
    #X_2 = np.empty_like(X)
    #for i in range(len(X)): 
    #    X_1[i] = (X[i] + 0.01)**(-1)
    #    X_2[i] = 100 if 1.0 - X[i] < 0.01 else (1.0 - X[i])**(-1)
    #XX = np.vstack((X,X_1,X_2)).T
    XX = X[:,np.newaxis]
    Y = projects[:,2]
    lr = linear_model.LogisticRegression()
    lr.fit(XX,Y)
    probas_simple.append(lr.predict_proba(XX))
    predict_simple.append(lr.predict(XX))
    const.append(lr.intercept_[0])
    alpha.append(lr.coef_[0][0])
    #alpha_1.append(lr.coef_[0][1])
    #alpha_2.append(lr.coef_[0][2])


pylab.plot(dates,const, label = "constant")
pylab.plot(dates,alpha, label = "linear")
pylab.plot(dates,alpha_1, label = "hyperbolic 0.01")
pylab.plot(dates,alpha_2, label = "hyperbolic 1 (cap 100)")
pylab.legend()
pylab.show()

### Observations:   - pretty stable
#                   - magnitude 

###Assessing the stability of predictors

const = []
alpha = []
alpha_1 = []
alpha_2 = []
probas_simple = []
predict_simple = []
dates = [10*i - 1 for i in range(1,101)]
for date in dates:
    X = statuses[:,date,1]
    X_1 = np.empty_like(X)
    X_2 = np.empty_like(X)
    for i in range(len(X)): 
        X_1[i] = (X[i] + 0.01)**(-1)
        X_2[i] = 100 if 1.0 - X[i] < 0.01 else (1.0 - X[i])**(-1)
    XX = np.vstack((X,X_1,X_2)).T
    #XX = X[:,np.newaxis]
    Y = projects[:,2]
    lr = linear_model.LogisticRegression()
    lr.fit(XX,Y)
    probas_simple.append(lr.predict_proba(XX))
    #const.append(lr.intercept_[0])
    #alpha.append(lr.coef_[0][0])
    #alpha_1.append(lr.coef_[0][1])
    #alpha_2.append(lr.coef_[0][2])


TV1 = np.empty_like(statuses[:,0,1])
for i in range(len(probas)-1):
    Xt = probas_simple[i][:,0]
    Xtplus1 = probas_simple[i+1][:,0]
    TV1 += np.abs(Xtplus1 - Xt)


i_max = np.argmax(TV1)
p_TVmax = []
res_TVmax = []
for i in range(len(probas_simple)):
    p_TVmax.append(probas_simple[i][i_max,1])
#    pred_TVmax.append(predict_simple[i][i_max])
    res_TVmax.append(statuses[:,dates[i],1][i_max])


pylab.plot(dates,p_TVmax)
pylab.plot(dates,res_TVmax)
pylab.grid(True)
pylab.xticks(np.arange(0,1000,100))
pylab.show()

i_min = np.argmin(TV1)
p_TVmin = []
pred_TVmin = []
res_TVmin = []
for i in range(len(probas_simple)):
    p_TVmin.append(probas_simple[i][i_min,1])
#    pred_TVmax.append(predict_simple[i][i_max])
    res_TVmin.append(statuses[:,dates[i],1][i_min])

pylab.plot(dates,p_TVmin)
#pylab.plot(dates,pred_TVmax)
pylab.plot(dates,res_TVmin)
pylab.grid(True)
pylab.xticks(np.arange(0,1000,100))
pylab.show()


###Looking for money lost
money_lost = np.zeros_like(statuses[:,0,1])
dates_loss = np.zeros_like(statuses[:,0,1])
for i in range(len(probas)-1):
    Xt = statuses[:,dates[i],1]
    Xtplus1 = statuses[:,dates[i+1],1]
    
        if dates_loss[j] == 0. and  Xtplus1[j] < Xt[j]: dates_loss[j] = dates[i]


###Taking tweets into account


