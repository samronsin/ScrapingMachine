# -*- coding: utf-8 -*-

import sys
from numpy import *
import urllib
import re


def projects_list():
    webpage = urllib.urlopen('http://www.kickstarter.com/discover/advanced?sort=launch_date').read()
    projects_list_raw = re.findall(u'(/projects/)(.*)(\?ref=)' , webpage)
    n_projects = len(projects_list_raw)/2
    projects = list(arange(n_projects))
    for i in arange(n_projects):
        projects[i] = projects_list_raw[2*i][1]
    return projects

projects_list()
