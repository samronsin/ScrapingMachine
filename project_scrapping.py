# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

import sys, os, re, unicodedata, json, urllib, datetime
from numpy import *
import BeautifulSoup

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

def project_id(project_page):
    return int(re.search(u'(window.current_project = \"{&quot;id&quot;:)([0-9]+)(,&quot;name&quot;)', project_page).groups()[1])

def creator_name(project_page):
 return re.search(u'data-modal-title=\"Biography\" id=\"name\">(.*)<', project_page).groups()[0]

def project_title(project_page):
    return re.search(u'(class=\"NS-project_-running_board\">\n<h2 id=\"title\">\n<a href=\"\/projects\/)(.*)(\">)(.*)(<)' , project_page).groups()[3]

def nb_backers(project_page):
    return int(re.search(u'(\"Project\[backers_count\]\">)([0-9]+)' , project_page).groups()[1])
 
def project_status(project_page):
    status_string = re.search(u'(<div data-project-state=\")(.*)(\" id=\"about\">)', project_page).groups()[1]
    if status_string == 'successful':
        status = 1
    elif status_string == 'live':
        status = 0
    elif status_string == 'failed':
        status = -1
    elif status_string == 'submitted':
        status = -2
    elif status_string == 'suspended':
        status = -3
    elif status_string == 'canceled':
        status = -4
    else:
        status = -5 #undefined status ('submitted'?)
    return status


def project_goal(project_page):
    return float(re.search(u'(data-goal=\")([0-9]+\.[0-9]+)', project_page).groups()[1]) 

def project_money(project_page):
    return float(re.search(u'(data-pledged=\")([0-9]+\.[0-9]+)', project_page).groups()[1])

def nb_rewards(project_page):
    return int(re.search(u'(data-reward-count=\")([0-9]+)', project_page).groups()[1])

def currency(project_page):
    return re.search(u'(data-currency=\")(.*)(\" data-format=\"shorter_money\")', project_page).groups()[1] 

def rewards_list(project_page):
    rewards_list_raw = re.findall(u'(Pledge\n<span class=\")(.*)(\">)(.*)(</span>)', project_page)
    n = len(rewards_list_raw)
    rewards_list = []
    for i in arange(n) :
        rewards_list.append(parse_raw_int(rewards_list_raw[i][3].replace('€','').replace('$','').replace('£','')))
    return rewards_list

def max_rewards_list(project_page):
    rewards_list_raw = re.findall(u'(Pledge\n<span class=\")(.*)(\">)(.*)(</span>)', project_page)
    n = len(rewards_list_raw)
    rewards_list = []
    for i in arange(n) :
        rewards_list.append(parse_raw_int(rewards_list_raw[i][3].replace('€','').replace('$','').replace('£','')))
    return rewards_list

def backers_list(project_page):
    backers_list_raw = re.findall(u'(span class="num-backers mr1">\n)([0-9]*.*[0-9]+)',project_page)
    n = len(backers_list_raw)
    backers_list = []
    for backer_raw in backers_list_raw :
        backers_list.append(parse_raw_int(backer_raw[1]))
    return backers_list

def has_video(project_page):
    return int(bool(re.search(u'(<div data-has-video=\")(.*)(\" id="video-section">)', project_page).groups()[1]))

def category(project_page):
    return re.search(u'(<li class=\"category\" data-project-parent-category=\")(.*)(\">\n<a class=\"grey-dark\")',project_page).groups()[1].replace(' &amp; ','')

def duration(project_page):
    return float(re.search(u'(<span data-duration=\")(.*)(\" data-end_time)', project_page).groups()[1])

def fb_connected(project_page):
    try: 
        re.search(u'<li class=\"facebook-connected\">',project_page).group()
        res = 1
    except:
        res = 0
    return res

#def tw_connected(project_page):
#    try: 
#        re.search(u'<li class=\"twitter-connected\">',project_page).group()
#        res = 1
#    except:
#        res = 0
#    return res

def has_links(project_page):
    try: 
        re.search(u'<li class=\"links\">',project_page).group()
        res = 1
    except:
        res = 0
    return res

def nb_backed(project_page):
    try:
        n = int(re.search(u'(<a class=\"green-dark bold more-button remote_modal_dialog\" data-modal-title=\"Projects backed by )(.*)(\" href=\"/profile/)(.*)(/backed\">)(.*)( backed)',project_page).groups()[5])
    except:
        n = 0
    return n

def nb_created(project_page):
    try:
        n = int(re.search(u'(<a class=\"green-dark bold more-button remote_modal_dialog\" data-modal-title=\"Projects created by )(.*)(\" href=\"/profile/)(.*)(/created\">)(.*)( created)',project_page).groups()[5])
    except:
        n = 0
    return n

def len_description(project_page):
    soup = BeautifulSoup.BeautifulSoup(project_page)
    desc = soup.findAll("div", { "class" : "full-description" })
    return float(len(str(desc).split()))

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



#current_vars=["scrapping_day", "scrapping_time", "project_title" ,"nb_backers" ,"project_goal" ,"project_money" ,"nb_rewards", "rewards_list" ,"nb_backers_list", "creator_name"]

    
#update_file('lalorek/a-field-guide-to-silicon-hills', current_vars)
#print_info(webpage, current_vars)
