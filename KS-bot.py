# -*- coding: utf-8 -*-

import urllib, re, time
from datetime import datetime, timedelta

import sqlalchemy

from sqlalchemy import create_engine, update, MetaData, Table, Column, Integer, String

engine = create_engine('mysql://root:bordeldemerde@localhost:5432/axplusbdb')
metadata = MetaData(bind = engine)
campaign = Table('campaign', metadata, autoload=True)


def get_campaigns_url_list():
    """ Get the raw list of 20 projects from 'ending soon' page """
    url = 'https://www.kickstarter.com/discover/advanced?sort=end_date'
    html_data = urllib.urlopen(url).read()
    campaigns_list_raw = re.findall(u'(/projects/)(.*)(\?ref=)', html_data)
    campaigns_list = []
    for i in range(len(campaigns_list_raw)/2):
        campaigns_list.append(campaigns_list_raw[2*i][1])
    return campaigns_list


def get_html_data(short_url):
    url = 'https://www.kickstarter.com/projects/' + short_url
    html_data = urllib.urlopen(url).read()
    return html_data


def augment_db(campaigns_list):
    for short_url in campaigns_list:
        res = campaign.select().where(campaign.c.short_url == short_url).execute()
        #unrecorded campaign
        if res.rowcount == 0:
            html_data = get_html_data(short_url)
            campaign_ended = is_campaign_ended(html_data)
            #non yet ended campaign
            if not(campaign_ended):
                campaign_data = get_live_campaign_data(html_data)
                campaign_data["short_url"] = short_url
                campaign.insert(campaign_data).execute()
            else:
                print "problem: " + short_url


def update_db():
    res = campaign.select().where(campaign.c.ended == False).execute()
    for row in res:
        short_url = row['short_url']
        html_data = get_html_data(short_url)
        campaign_ended = is_campaign_ended(html_data)
        if campaign_ended:
            campaign_data = get_ended_campaign_data(html_data)
            campaign.update().where(campaign.c.short_url == short_url).values(campaign_data).execute()
        else:
            campaign_data = get_live_campaign_data(html_data)
            campaign.update().where(campaign.c.short_url == short_url).values(campaign_data).execute()


def is_campaign_ended(html_data):
    search = re.search(u'(Project-ended-true)', html_data)
    return (search != None)


def get_live_campaign_data(html_data):
    goal = float(re.search(u'(data-goal=\")([0-9]+\.[0-9]+)', html_data).groups()[1])
    raised = float(re.search(u'(data-pledged=\")([0-9]+\.[0-9]+)', html_data).groups()[1])
    n_backers = int(re.search(u'(backers_count&quot;:)([0-9]+)', html_data).groups()[1])
    str_end_date = re.search(u'(data-end_time=\")(.*)(\" data-hours-remaining)', html_data).groups()[1]
    date, time_zone = str_end_date.split('T')
    time, zone = time_zone.split('-')
    end_date = datetime.strptime(date + "T" + time, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=int(zone.split(":")[0]))
    currency = re.search(u'(data-currency=\")(.*)(\" data-format)', html_data).groups()[1]
    return {"goal": goal, "raised": raised, "n_backers": n_backers, "end_date": end_date, "currency": currency, "ended": False}


def get_ended_campaign_data(html_data):
    raised = float(re.search(u'(pledged&quot;:)([0-9]+\.[0-9]+)', html_data).groups()[1])
    n_backers = int(re.search(u'(backers_count&quot;:)([0-9]+)', html_data).groups()[1])
    return {"n_backers": n_backers, "raised": raised, "ended": True}


def ended_campaign_data(html_data):
    goal = float(re.search(u'(data-goal=\")([0-9]+\.[0-9]+)', html_data).groups()[1])
    raised = float(re.search(u'(data-pledged=\")([0-9]+\.[0-9]+)', html_data).groups()[1])
    str_end_date = re.search(u'(data-end_time=\")(.*)(\" data-hours-remaining)', html_data).groups()[1]
    date, time_zone = str_end_date.split('T')
    time, pm, zone = re.split(u'([\+,\-])', time_zone)
    eps = -1 if pm == "+" else 1
    end_date = datetime.strptime(date + "T" + time, "%Y-%m-%dT%H:%M:%S") + eps * timedelta(hours=int(zone.split(":")[0]))
    currency = re.search(u'(data-currency=\")(.*)(\" data-format)', html_data).groups()[1]
    return {"short_url": short_url, "goal": goal, "raised": raised, "end_date": end_date, "currency": currency}


if __name__ == '__main__':
    while(True):
        campaigns_list = get_campaigns_url_list()
        augment_db(campaigns_list)
        update_db()
        time.sleep(300)

