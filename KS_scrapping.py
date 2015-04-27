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


#update (March 2015)
url_new = 'https://www.kickstarter.com/discover/advanced?sort=newest'
#url_new = 'http://www.kickstarter.com/discover/advanced?sort=launch_date'



def random_pages(n_pages):
""" Get uniformly distributed n_pages random pages (containing each 20 KS campaigns)
    NB (July 5th 2014)
    pages 0 - 251 -> live projects (should be +/- stable in the short term)
    pages 252 - 3484 -> successful projects (NOT stable in the short term -> UPDATE)
    pages 3485 - 7031 -> unsuccessful projects (NOT stable in the short term -> UPDATE)
    pages 7031 - 7684 -> canceled projects
    pages 7684 - 7691 -> suspended projects """
    start = 252
    end = 7031 # get rid of canceled and suspended projects
    N = end - start
    n_pages = n_pages 
    epsilon = 0.5 * n_pages / N
    rand_finished = False
    while(not(rand_finished)):
        sigma = 0.0
        rand_raw = []
        for i in range(n_pages + 1):
            delta = epsilon + (1 - epsilon)*random.random() # NB: not perfectly uniform, but much more efficient...
            sigma += delta
            rand_raw.append(sigma)
        rand_raw.pop()
        rand_pages = []
        count = 0
        rand_finished = True
        for r in rand_raw:
            r_page = start + int(r * N / sigma) # convert the increments to fit the (start-end) range
            try:
                # make sure the same page does not appear twice
                if(r_page > rand_pages[-1]):
                    rand_pages.append(r_page)
                else:
                    # start over
                    rand_finished = False
                    break
            except:
                rand_pages.append(r_page) # rand_pages is an empty list
    return rand_pages


def projects_list(url):
""" Get the raw list of 20 projects from a page """
    webpage = urllib.urlopen(url).read()
    projects_list_raw = re.findall(u'(/projects/)(.*)(\?ref=)', webpage)
    n_projects = len(projects_list_raw)/2 #getting rid of the redundancy
    projects = list(range(n_projects))
    for i in range(n_projects):
        projects[i] = projects_list_raw[2*i][1] #getting rid of the redundancy
    return projects


def parallel_run(fn, l):
   for i in l:
       Thread(target = fn, args = (i,)).start()


def projects_scanner(remaining, rejected):
""" remaining is the list of pages with unattempted HTTP requests
    rejected is the list of pages with rejected HTTP requests
    projects_scanner """
    lock = Lock()
    def scrape(project):
        project_url = 'http://www.kickstarter.com/projects/' + project
        project_page = urllib.urlopen(project_url).read()
        with lock:
            try:
                # get the all data from the page (if HTTP request accepted)
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
                # /!\ print is not thread safe!
                s = str(project) + " " + str(pid) + " " + str(goal) + " " + str(curr) + " " + str(status) + " " + str(nrwds) + " " + str(video) + " " + str(category) + " " + str(duration) + " " + str(fb) + " " + str(links) + " " + str(backed) + " " + str(created) + " " + str(desc) + " " + str(lrwds).replace(' ','') + " " + str(lbackers).replace(' ','')
                sys.stdout.write(s + '\n')
                try:
                    # remove the project from the list of rejected requests (if it was in that list in the first place)
                    rejected.remove(project)
                except:
                    # the project was not in the list of rejected requests
                    pass
            except:
                # HTTP request denied: put the project in the list of rejected requests
                rejected.append(project)
    parallel_run(scrape, remaining + thrown)


if __name__ == '__main__':
    url_end_rad = 'https://www.kickstarter.com/discover/ending-soon?ref=ending_soon&page='
    # get 10000 projects ~ uniformly distributed
    pages = random_pages(500)
    rejected = []
    for page in pages:
        url_end = url_end_rad + str(page)
        projects = projects_list(url_end)
        projects_scanner(projects, rejected)



