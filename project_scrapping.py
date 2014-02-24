# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

import sys, os, re, unicodedata, json, urllib, datetime
from numpy import *

#TODO:
#  - adapt the writing to files to write incrementally the relevant information
#  - replace regex calls by XPath
#  - one single parsing of the project page to get all the info
#  - replace the calls to print (on the screen) by writing on a DB
#  - refléchir à l'optimisation de l'ouverture de page (L17), qui prend plus d'une seconde
#  - ajouter d'autres  
#  - récupérer le type de l'erreur au lieu de relever simplement 'erreur' L100


#webpage = urllib.urlopen('http://www.kickstarter.com/projects/lalorek/a-field-guide-to-silicon-hills').read()


#### Fonctions de nettoyage de données
#########################################################


def parse_raw_int(s):
    new_s = s.replace(",", "")
    return int(new_s)


def clean_varnames(var): return var.upper().replace('_',' ')


#### Fonctions pour chercher les informations sur la page
#########################################################

def creator_name(project_page):
 return re.search(u'data-modal-title=\"Biography\" id=\"name\">(.*)<', project_page).groups()[0]

def project_title(project_page):
    return re.search(u'(class=\"NS-project_-running_board\">\n<h2 id=\"title\">\n<a href=\"\/projects\/)(.*)(\">)(.*)(<)' , project_page).groups()[3]

def nb_backers(project_page):
    return int(re.search(u'(\"Project\[backers_count\]\">)([0-9]+)' , project_page).groups()[1])
 
###bon ca se buggue va savoir, je le retire aussi de la liste L101
#def project_status(project_page):
#    return re.search(u'(Project-state-)(.*)( Project-is)', project_page).groups()[1] 

def project_goal(project_page):
    return float(re.search(u'(data-goal=\")([0-9]+\.[0-9]+)', project_page).groups()[1])
 

def project_money(project_page):
    return float(re.search(u'(data-pledged=\")([0-9]+\.[0-9]+)', project_page).groups()[1])

def nb_rewards(project_page):
    return int(re.search(u'(data-reward-count=\")([0-9]+)',project_page).groups()[1])
 
def nb_rewards(project_page):
    return int(re.search(u'(data-reward-count=\")([0-9]+)', project_page).groups()[1])
 

def rewards_list(project_page):
    rewards_list_raw = re.findall(u'(<h5>\nPledge\n<span class=\"money usd \">\$)([0-9]*.*[0-9]+)', project_page)
    n = len(rewards_list_raw)
    rewards_list = list(arange(n))
    for i in arange(n) :
        rewards_list[i] = parse_raw_int(rewards_list_raw[i][1])
    return rewards_list

def nb_backers_list(project_page):
    nb_backers_list_raw = re.findall(u'(span class="num-backers">\n)([0-9]*.*[0-9]+)',project_page)
    n = len(nb_backers_list_raw)
    nb_backers_list = list(arange(n))
    for i in arange(int(n)) :
        nb_backers_list[i] = parse_raw_int(nb_backers_list_raw[i][1])
    return nb_backers_list



#### Fonctions d'output
#########################################################

def scrapping_day(project_page): return str(datetime.datetime.now().date())

def scrapping_time(project_page): return str(datetime.datetime.now())


def print_info(project_page, list_var):
    for var in list_var:
        print "%s : \t %s" %(clean_varnames(var), globals()[var](project_page)) #globals() est un dictionnaire de toutes les fonctions créés dans la session, il associe le nom de la fonction à la fonction

def update_file(project_name, list_var):
    if not(os.path.exists('KSprojects')):
        os.mkdir('KSprojects')
    path ='KSprojects/' + project_name.replace('/','@')
    project_page = urllib.urlopen('http://www.kickstarter.com/projects/' + project_name).read()
    if not(os.path.exists(path)):
        file = open(path, 'a')
    else: file = open(path,'w+')
    for var in list_var:
        file.write("%s : \t %s\n" %(clean_varnames(var), globals()[var](project_page)))
    file.close()

def get_data(project_page, list_var):
    data={}  #on crée un dictionnaire qui associera à chaque var de list_var, sa valeur dans projectpage
    for var in list_var:
        try :
            data[clean_varnames(var)] = globals()[var](project_page)
        except :
            data[clean_varnames(var)] = 'error' #ici changer pour obtenir le type de l'erreur
    return data



current_vars=["scrapping_day", "scrapping_time", "project_title" ,"nb_backers" ,"project_goal" ,"project_money" ,"nb_rewards", "rewards_list" ,"nb_backers_list", "creator_name"]

    
#update_file('lalorek/a-field-guide-to-silicon-hills', current_vars)
#print_info(webpage, current_vars)
