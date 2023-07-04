#!/usr/bin/env python3
from bs4 import BeautifulSoup
import datetime
import ics
import pytz
import requests

cal = ics.Calendar()
cal.creator = "codygarver"
cal.name = "Pokemon Go Events"
cal.timezone = "US/Eastern"

cal_filename = "pokemon-go-events.ics"

url = "https://leekduck.com"

page = requests.get(url + "/events/")

soup = BeautifulSoup(page.content, 'html.parser')

spans = soup.find_all('span', class_='event-header-item-wrapper')

# Read existing events from file
existing_event_urls = []
with open(cal_filename, 'r') as existing_cal_file:
    existing_cal = ics.Calendar(existing_cal_file.read())
    for existing_cal_event in existing_cal.events:
        existing_event_urls.append(existing_cal_event.url)

for span in spans:
    link = url + span.find('a', class_='event-item-link', href=True)['href']
    if link in existing_event_urls:
        continue
    cal_event = ics.Event()
    cal_event.url = link
    h2 = span.find('h2')
    cal_event.name = h2.text
    begin_date = soup.find("h5", class_="event-header-time-period")["data-event-start-date-check"]
    begin_date_local = datetime.datetime.strptime(begin_date, "%Y-%m-%dT%H:%M:%S%z")
    begin_date_local = begin_date_local.astimezone(pytz.timezone('US/Eastern'))
    # Subtract 12 hours from begin_date_local
    begin_date_local = begin_date_local - datetime.timedelta(hours=12)
    cal_event.begin = begin_date_local
    end_date = soup.find("h5", class_="event-header-time-period")["data-event-end-date"]
    end_date_local = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S%z")
    end_date_local = end_date_local.astimezone(pytz.timezone('US/Eastern'))
    cal_event.end = end_date_local
    # Subtract 12 hours from end_date_local
    end_date_local = end_date_local - datetime.timedelta(hours=12)
    cal_event.dtstamp = datetime.datetime.now()
    cal.events.add(cal_event)

with open(cal_filename, 'w') as cal_file:
    cal_file.writelines(cal)