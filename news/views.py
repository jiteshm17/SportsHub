import time

from django.shortcuts import render
import requests
from datetime import datetime

requests.packages.urllib3.disable_warnings()
from bs4 import BeautifulSoup
from .models import HeadLine, LastNewsUpdate
from sports.models import Sport_Info


def scrape_all_sports():
    session = requests.session()
    all_sports = Sport_Info.objects.all()
    sports_list = ['sports']
    for sport in all_sports:
        sports_list.append(sport.name)
    HeadLine.objects.all().delete()
    for sport in sports_list:
        url = "https://news.google.com/search?q=" + sport + "&hl=en-IN&gl=IN&ceid=IN%3Aen"
        content = session.get(url, verify=False).content

        soup = BeautifulSoup(content, "html.parser")

        posts = soup.find_all('div', {'class': 'NiLAwe y6IFtc R7GTQ keNKEd j7vNaf nID9nc'})
        for i in posts:
            new_healine = HeadLine()
            try:
                title = i.find_all('a', {'class': 'DY5T1d'})[0].text
                new_healine.title = title
            except:
                continue
            try:
                link = i.find_all('a', {'class': 'DY5T1d'})[0]['href']
                link = "https://news.google.com" + link
                new_healine.url = link
            except:
                pass
            try:
                img = i.find('img', {'class': 'tvs3Id QwxBBf'})['src']
                new_healine.image_url = img
            except:
                pass
            try:
                site = i.find('a', {'class': 'wEwyrc AVN2gc uQIVzc Sksgp'}).text
                new_healine.site = site
            except:
                pass
            try:
                time = i.find('time', {'class': 'WW6dff uQIVzc Sksgp'}).text
                new_healine.time = time
            except:
                pass

            new_healine.category = sport
            new_healine.save()


def news_list(request):
    now = datetime.now()
    last_update = LastNewsUpdate.objects.all()
    if len(last_update) == 0:
        scrape_all_sports()
        LastNewsUpdate.objects.create(last_update=datetime.now())
    else:
        last_updated_time = time.mktime(last_update[0].last_update.timetuple())
        current_time = time.mktime(now.timetuple())
        if (int(current_time - last_updated_time) / 60) > 10000000:
            scrape_all_sports()
            LastNewsUpdate.objects.all().delete()
            LastNewsUpdate.objects.create(last_update=datetime.now())
    all_sports = Sport_Info.objects.all()
    sports_list = []
    for sport in all_sports:
        sports_list.append(sport.name)
    context = {}
    for sport in sports_list:
        news = HeadLine.objects.filter(category=sport)
        slider_1 = news[:4]
        slider_2 = news[4:8]
        blog_1 = news[8:12]
        n = 4
        slider_3 = [news[i * n:(i + 1) * n] for i in range((len(news[13:]) + n - 1) // n)]
        sport_details = all_sports.get(name=sport)
        icon = sport_details.icon
        context[sport] = {'slider_1': slider_1, 'slider_2': slider_2, 'slider_3': slider_3, 'blog_1': blog_1,
                          'icon': icon}
    return render(request, 'news/news_list.html', {'context': context, 'News': 'active'})
