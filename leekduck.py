#!/usr/bin/env python3
from bs4 import BeautifulSoup
import datetime
import icalendar
import pytz
import requests

cal = icalendar.Calendar()
cal.add('prodid', '-//leekduck.com//NONSGML Events//EN')
cal.add('version', '2.0')


url = "https://leekduck.com"

page = requests.get(url + "/events/")

soup = BeautifulSoup(page.content, 'html.parser')

spans = soup.find_all('span', class_='event-header-item-wrapper')

for span in spans:
    h2 = span.find('h2')
    cal_event = icalendar.Event()
    cal_event.add('summary', h2.text)
    begin_date = soup.find("h5", class_="event-header-time-period")["data-event-start-date-check"]
    begin_date_local = datetime.datetime.strptime(begin_date, "%Y-%m-%dT%H:%M:%S%z")
    begin_date_local = begin_date_local.astimezone(pytz.timezone('US/Eastern'))
    # Subtract 12 hours from begin_date_local
    begin_date_local = begin_date_local - datetime.timedelta(hours=12)
    cal_event.add('dtstart', begin_date_local)
    end_date = soup.find("h5", class_="event-header-time-period")["data-event-end-date"]
    end_date_local = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S%z")
    end_date_local = end_date_local.astimezone(pytz.timezone('US/Eastern'))
    cal_event.add('dtend', end_date_local)
    # Subtract 12 hours from end_date_local
    end_date_local = end_date_local - datetime.timedelta(hours=12)
    link = span.find('a', class_='event-item-link', href=True)
    cal_event.add('url', url + link['href'])
    cal.add_component(cal_event)

cal_file = open('pokemon-go-events.ics', 'wb')
cal_file.write(cal.to_ical())
cal_file.close()