import requests
from bs4 import BeautifulSoup
import sqlite3

"""Parser output of data in sqlite3 + uniqueness check"""

url = 'https://animevost.org/ongoing/page/1/'

def site_snapshot(url):
    headers = {'User-agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def check_main_block(snapshot,main_block, *args):
    array_search = snapshot.find_all(main_block, class_=args)
    return array_search


def pull_all(url):
    mainD = []
    for i in check_main_block(site_snapshot(url), 'div', 'shortstoryHead'):
        lowD = None
        # anime name
        for ii in check_main_block(i, 'a'):
            lowD = ii.text.split(' /')[0]
            print(ii.text.split(' /')[0])
        mainD.append(lowD)
    return mainD

def writen(lowD):
    conn = sqlite3.connect('chat.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
       text INT PRIMARY KEY,
       step2 TEXT);
    """)
    conn.commit()

    query = """INSERT INTO users(text, step2)
       VALUES(?, ?);"""
    for i in lowD:
        try:
            cur.execute(query, i)
            conn.commit()
        except:
            print('Уже в БД')



listDate = pull_all(url)
soup = site_snapshot(url)


for i in soup.find_all('td', class_ = 'block_4'):
    href_search = i.find_all('a')

for i in href_search:
    peg = i.get('href')
    Date = pull_all(peg)
    listDate = listDate + Date
#print(listDate)
#writen(listDate)



