# -*- coding: utf-8 -*-

import sys
from numpy import *
import urllib
import re


#to do list:
#- savoir si la short url est stable ou non, pas sur vu qu'elle inclut l'identifiant du créateur, qui peut décider 
#de prendre à un moment un pseudo

def projects_list():
    """Récupère la liste brute des nouveaux projets
    ne poursuis pas au delà des 20 premiers projets 
    (cf bouton 'load more' qu'on n'active pas)"""
    webpage = urllib.urlopen('http://www.kickstarter.com/discover/advanced?sort=launch_date').read()
    projects_list_raw = re.findall(u'(/projects/)(.*)(\?ref=)' , webpage)
    n_projects = len(projects_list_raw)/2
    projects = list(arange(n_projects))
    for i in arange(n_projects):
        projects[i] = projects_list_raw[2*i][1]
    return projects

#print projects_list()
#on crée la liste des projets, ( identifiant, short_url), en vérifiant bien que la short url n'est pas dans la liste

with open('list_projects.txt', 'r+') as list_projects_file :  #la syntaxe 'with ... as :' permet d'éviter d'oublier un file.close, le fichier est automatique fermé en sortie de boucle    
    if len(list_projects_file.read()) == 0 :
        data = [[]]
        list_urls = []
        next_id = 0
    else :	
    	list_projects_file.seek(0) # c'est là le trick: on a déjà lu le fichier l29, il faut rembobiner le fichier pour pouvoir le relire sinon il lira ce qu'il y a la suite de la fin, cad rien!
        data      =  [ project.strip().split(';') for project in list_projects_file.readlines() ]
        list_urls =   [ project[1] for project  in data ]   # data[:,1] ne marche pas c'est génial
        list_id   =  [float(project[0]) for project  in data ]
        next_id = int(max(list_id ) + 1)

    for new_project_url in projects_list() :
        if new_project_url not in list_urls :
            list_projects_file.write( str(next_id) + ';' + new_project_url +  '\n') 
            next_id += 1    