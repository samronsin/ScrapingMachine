# -*- coding: utf-8 -*-

import sys, os, urllib, re
from numpy import *

#to do list:
#- check whether short url is stable on KS (NB: includes campaigner's login)
#-> on the profile editing page: "You can set a vanity URL here. Once set, this vanity URL can not be changed."

def projects_list():
    #Gets the raw list of new projects
    #Only gets the 20 newest projects
    #('load more' button not activated)
    webpage = urllib.urlopen('http://www.kickstarter.com/discover/advanced?sort=launch_date').read()
    projects_list_raw = re.findall(u'(/projects/)(.*)(\?ref=)', webpage)
    n_projects = len(projects_list_raw)/2 #getting rid of the redundancy
    projects = list(range(n_projects))
    for i in range(n_projects):
        projects[i] = projects_list_raw[2*i][1] #getting rid of the redundancy
    return projects

#print projects_list()
#on crée la liste des projets, (identifiant, short_url), en vérifiant bien que la short url n'est pas dans la liste
if not(os.path.exists('list_projects.txt')):
    open('list_projects.txt', 'a').close()


with open('list_projects.txt', 'w+') as list_projects_file :  #la syntaxe 'with ... as :' permet d'éviter d'oublier un file.close, le fichier est automatique fermé en sortie de boucle    
    if len(list_projects_file.read()) == 0 :
        data = [[]]
        list_urls = []
        next_id = 0
    else :	
        list_projects_file.seek(0) # c'est là le trick: on a déjà lu le fichier l29, il faut rembobiner le fichier pour pouvoir le relire sinon il lira ce qu'il y a la suite de la fin, cad rien!
        data      =  [ project.strip().split(';') for project in list_projects_file.readlines() ]
        list_urls =   [ project[1] for project  in data ]   # data[:,1] ne marche pas c'est génial
        list_id   =  [float(project[0]) for project  in data ]
        #next_id = int(max(list_id ) + 1)
    for new_project_url in projects_list() :
        if new_project_url not in list_urls :
            list_projects_file.write(
            # str(next_id) + ';' + 
            # seems useless
            new_project_url + '\n' )
            new_project_filename = new_project_url.replace('/','@')
            if not(os.path.exists('KSprojects')):
                os.mkdir('KSprojects')
            path = 'KSprojects/' + new_project_filename
            open(path, 'a').close()
            next_id += 1


