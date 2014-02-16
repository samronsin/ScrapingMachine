# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

import project_scrapping as pj
import urllib



with open('list_projects.txt', 'r') as list_projects_file : 
    list_projects= [project.strip().split(';') for project in list_projects_file ]

def projects_scanner(list_projets):
    all_project = {}
    for project in list_projets :
        id , short_url = project
        long_url = 'http://www.kickstarter.com/projects/'+short_url
        project_page_contents = urllib.urlopen(long_url).read()
        data_project = pj.get_data(project_page_contents , pj.current_vars)
        id_date = id + '_' + data_project['SCRAPPING DAY']
        all_project[id_date] = data_project
    return all_project


if __name__ == '__main__' :
	for key, data in projects_scanner(list_projects).items():
		print 'id is %s and data is %s' %(key, data)