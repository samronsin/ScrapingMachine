# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

import sys
from numpy import *
import re
import unicodedata
import json
import urllib
#TODO:
#  - replace regex calls by XPath
#  - one single parsing of the project page to get all the info
#  - replace the calls to print (on the screen) by writing on a DB
#  - refléchir à l'optimisation de l'ouverture de page (L17), qui prend plus d'une seconde
#  - ajouter d'autres 


webpage = urllib.urlopen('http://www.kickstarter.com/projects/lalorek/a-field-guide-to-silicon-hills').read()
#print webpage

project_head = re.search(u'(class=\"NS-project_-running_board\">\n<h2 id=\"title\">\n<a href=\"\/projects\/)(.*)(\">)(.*)(<)' , webpage)
href = project_head.groups()[1]
project_title = project_head.groups()[3]


def project_title(project_page):
    return re.search(u'(class=\"NS-project_-running_board\">\n<h2 id=\"title\">\n<a href=\"\/projects\/)(.*)(\">)(.*)(<)' , project_page).groups()[3]

def nb_backers(project_page):
<<<<<<< HEAD
    return int(re.search(u'(\"Project\[backers_count\]\">)([0-9]+)' , project_page).groups()[1])
=======
    return int(re.search(u'(\"Project\[backers_count\]\">)([0-9]+)', project_page).groups()[1])
>>>>>>> b7597221a0fec58a0408873986ae08f11ab9723a

def project_status(project_page):
    return re.search(u'(Project-state-)(.*)( Project-is)', project_page).groups()[1]

def project_goal(project_page):
    return float(re.search(u'(data-goal=\")([0-9]+\.[0-9]+)', project_page).groups()[1])
<<<<<<< HEAD


def project_money(project_page):
    return float(re.search(u'(data-pledged=\")([0-9]+\.[0-9]+)', project_page).groups()[1])

def nb_rewards(project_page):
    return int(re.search(u'(data-reward-count=\")([0-9]+)',project_page).groups()[1])
=======

def nb_rewards(project_page):
    return int(re.search(u'(data-reward-count=\")([0-9]+)', project_page).groups()[1])
>>>>>>> b7597221a0fec58a0408873986ae08f11ab9723a

def parse_raw_int(s):
    new_s = s.replace(",", "")
    return int(new_s)

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

def clean(var): return var.upper().replace('_',' ')


<<<<<<< HEAD
current_vars=["project_title" ,"nb_backers" ,"project_status" ,"project_goal" ,"project_money" ,"nb_rewards" ,"parse_raw_int" ,"rewards_list" ,"nb_backers_list"]
def print_info(project_page, list_var):
    for var in list_var:
        print "%s : \t %s" %(clean(var), globals()[var](project_page)) #globals() est un dictionnaire de toutes les fonctions créés dans la session, il associe le nom de la fonction à la fonction

def get_data(project_page, list_var)
    data={}                                 #on crée un dictionnaire qui associera à chaque var de list_var, sa valeur dans projectpage
    for var in list_var:
        data[clean(var)] = globals()[var](project_page)
    return data
=======
def print_info(project_page):
    print "title: \'"+project_title(project_page)+"\'"
    print "goal: "+str(project_goal(project_page))
    print str(nb_rewards(project_page))+" rewards"
    print rewards_list(project_page)
    print str(nb_backers(project_page))+" backers"
    print nb_backers_list(project_page)
>>>>>>> b7597221a0fec58a0408873986ae08f11ab9723a

    
print_info(webpage, current_vars)
