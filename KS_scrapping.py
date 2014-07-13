# -*- coding: utf-8 -*-

import sys, os, urllib, re
import peewee
from peewee import *
import numpy
from numpy import *
import project_scrapping as ps
import time
from datetime import datetime, timedelta
from threading import Thread, Lock
import random


#to do list:
#- check whether short url is stable on KS (NB: includes campaigner's login)
#-> on the profile editing page: "You can set a vanity URL here. Once set, this vanity URL can not be changed."

#url_new = 'http://www.kickstarter.com/discover/advanced?sort=launch_date'

def random_pages(n_pages):
    start = 252
    end = 7031
    N = end - start
    n_pages = n_pages 
    epsilon = 0.5*n_pages/N
    rand_ok = False
    while(not(rand_ok)):
        sigma = 0.0
        rand_raw = []
        for i in range(n_pages + 1):
            delta = epsilon + (1-epsilon)*random.random() #NB: not perfectly uniform, but more efficient...
            sigma += delta
            rand_raw.append(sigma)
        rand_raw.pop()
        rand_pages = []
        count = 0
        rand_ok = True
        for r in rand_raw:
            r_page = 252 + int(r*N/sigma)
            try:
                if(r_page > rand_pages[-1]):
                    rand_pages.append(r_page)
                else:
                    rand_ok = False
                    break
            except:
                rand_pages.append(r_page) #empty list
    return rand_pages


def projects_list(url):
    #Gets the raw list of new projects
    #Only gets the 20 newest projects
    #('load more' button not activated)
    webpage = urllib.urlopen(url).read()
    projects_list_raw = re.findall(u'(/projects/)(.*)(\?ref=)', webpage)
    n_projects = len(projects_list_raw)/2 #getting rid of the redundancy
    projects = list(range(n_projects))
    for i in range(n_projects):
        projects[i] = projects_list_raw[2*i][1] #getting rid of the redundancy
    return projects

#print projects_list()
#on crée la liste des projets, (identifiant, short_url), en vérifiant bien que la short url n'est pas dans la liste
#if not(os.path.exists('list_projects.txt')):
#    open('list_projects.txt', 'a').close()


#with open('list_projects.txt', 'w+') as list_projects_file :  #la syntaxe 'with ... as :' permet d'éviter d'oublier un file.close, le fichier est automatique fermé en sortie de boucle    
#    if len(list_projects_file.read()) == 0 :
#        data = [[]]
#        list_urls = []
#        next_id = 0
#    else :	
#        list_projects_file.seek(0) # c'est là le trick: on a déjà lu le fichier l29, il faut rembobiner le fichier pour pouvoir le relire sinon il lira ce qu'il y a la suite de la fin, cad rien!
#        data      =  [ project.strip().split(';') for project in list_projects_file.readlines() ]
#        list_urls =   [ project[1] for project  in data ]   # data[:,1] ne marche pas c'est génial
#        list_id   =  [float(project[0]) for project  in data ]
#        #next_id = int(max(list_id ) + 1)
#    for new_project_url in projects_list() :
#        if new_project_url not in list_urls :
#            list_projects_file.write(
#            # str(next_id) + ';' + 
#            # seems useless
#            new_project_url + '\n' )
#            new_project_filename = new_project_url.replace('/','@')
#            if not(os.path.exists('KSprojects')):
#                os.mkdir('KSprojects')
#            path = 'KSprojects/' + new_project_filename
#            open(path, 'a').close()
#            next_id += 1

def parallel_run(fn, l):
   for i in l:
       Thread(target = fn, args = (i,)).start()

def projects_scanner(l,thrown):#,data):
    lock = Lock()
    def scrape(project):
        project_url = 'http://www.kickstarter.com/projects/' + project
        project_page = urllib.urlopen(project_url).read()
        with lock:
            try:                
                pid = ps.project_id(project_page)
                status = ps.project_status(project_page)
                nrwds = ps.nb_rewards(project_page)
                goal = ps.project_goal(project_page)
                curr = ps.currency(project_page)
                video = ps.has_video(project_page)
                category = ps.category(project_page)
                duration = ps.duration(project_page)
                fb = ps.fb_connected(project_page)
                links = ps.has_links(project_page)
                backed = ps.nb_backed(project_page)
                created = ps.nb_created(project_page)
                desc = ps.len_description(project_page)
                lrwds = ps.rewards_list(project_page)
                lbackers = ps.backers_list(project_page)
                #print project, pid, goal, curr, status, nrwds, video, category, duration, fb, links, backed, created, desc, str(lrwds).replace(' ',''), str(lbackers).replace(' ','')
                #/!\ print is not thread safe!
                s = str(project) + " " + str(pid) + " " + str(goal) + " " + str(curr) + " " + str(status) + " " + str(nrwds) + " " + str(video) + " " + str(category) + " " + str(duration) + " " + str(fb) + " " + str(links) + " " + str(backed) + " " + str(created) + " " + str(desc) + " " + str(lrwds).replace(' ','') + " " + str(lbackers).replace(' ','')
                sys.stdout.write(s + '\n')
                #data.append([project, pid, goal, curr, status, nrwds, video, category, duration, fb, links, backed, created, desc, str(lrwds).replace(' ',''), str(lbackers).replace(' ','')])
                #print data
                #print(len(data))
                try:
                    thrown.remove(project)
                    #print len(data), len(thrown)
                except:
                    pass
            except:
                thrown.append(project)
                #print len(data), len(thrown)
                #print 'failed scraping on ' + str(len(thrown)) + ' projects:'
                #print thrown
    parallel_run(scrape,l+thrown)
    #parallel_run(scrape,l[10:])


if __name__ == '__main__':
    url_end_rad = 'https://www.kickstarter.com/discover/ending-soon?ref=ending_soon&page='
    #NB (July 5th 2014)
    #pages 0 - 251 -> live projects (should be +/- stable in the short term)
    #pages 252 - 3484 -> successful projects (NOT stable in the short term -> UPDATE)
    #pages 3485 - 7031 -> unsuccessful projects (NOT stable in the short term -> UPDATE)
    #pages 7031 - 7684 -> canceled projects
    #pages 7684 - 7691 -> suspended projects
    #t0 = datetime.utcnow()
##    f = open('10000_random_campaigns.txt')
##    l = list(set(f.readlines()))
##    for line in l:
##        print line.replace('\n','')
#db = MySQLdb.connect(host="localhost", # your host, usually localhost
#                     user="root", # your username
#                      passwd="")
#cursor = db.cursor()
#sql = 'DROP DATABASE IF EXISTS `testdb`;'
#sql = 'CREATE DATABASE `testdb`;'
#cursor.execute(sql)

    pages = random_pages(500)
    #t1 = datetime.utcnow()
    #print (t1-t0).microseconds
    #t0 = datetime.utcnow()
    thrown = []
    #data = []
    for page in pages:
        #print 'scraping page ' + str(i)
        url_end = url_end_rad + str(page)
        projects = projects_list(url_end)
        projects_scanner(projects, thrown)#, data)
        #time.sleep(2)
    #print 'failed scraping on ' + str(len(thrown)) + ' projects'
    #print thrown
    #for project in thrown:
        #    project_url = 'http://www.kickstarter.com/projects/' + project
        #    project_page = urllib.urlopen(project_url).read()
        #    status = ps.project_status(project_page)
        #    pid = ps.project_id(project_page)
        #    nrwds = ps.nb_rewards(project_page)
        #    lrwds = ps.rewards_list(project_page)
        #    backers = ps.backers_list(project_page)
    #print dt



