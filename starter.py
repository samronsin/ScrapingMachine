# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

import project_scrapping as ps
import urllib
from threading import Thread

with open('list_projects.txt', 'r') as list_projects_file : 
    list_projects= [project.strip().split(';') for project in list_projects_file ]

#print list_projects

def parallel_run(fn, l):
       for i in l:
           Thread(target = fn, args = (i,)).start()


def projects_scanner(l):
    #all_projects = {}
    def update(project):
        id , short_url = project
        long_url = 'http://www.kickstarter.com/projects/' + short_url
        project_page_contents = urllib.urlopen(long_url).read()
        data_project = ps.get_data(project_page_contents , ps.current_vars)
        id_date = id + '_' + data_project['SCRAPPING DAY']
        #all_projects[id_date] = data_project
        print data_project
    parallel_run(update,l)


if __name__ == '__main__' :
	projects_scanner(list_projects)
