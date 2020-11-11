import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from random import randint
from random import choice

from config import Config

class OGUAutobumper:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'cookie': Config.cookie})
        self.main_url = "https://ogusers.com/"
        self.cached_threads = {}
        self.check_login()
        self._my_post_key = self.update_my_key()
        print("github.com/hell")
        print("OGUsers.com Autobumper\nReport any bugs/issues to au#0666\n")

    @property
    def my_post_key(self) -> str:
        return self._my_post_key

    def get_profile_link(self) -> str:
        response = self.session.get(self.main_url).text
        soup = BeautifulSoup(response, 'html.parser')
        userid = soup.find_all('a', class_='dropborder')
        for i in userid:
            if i.text == 'Profile':
                profile_link = i['href']
                userid = profile_link.split("https://ogusers.com/member.php?action=profile&uid=")[1]         
                print(profile_link, userid)    
        return profile_link, userid

    def get_info(self) -> str:
        response = self.session.get(self.main_url).text
        soup = BeautifulSoup(response, 'html.parser')
        username = soup.find('div', style=lambda value: value and 'font-size: 17px;' in value and 'font-weight: 600;' in value).text
        cred = soup.find('span', style=lambda value: value and 'padding: 0px 6px;' in value).text
        stats = soup.find_all('a', style='color:green')
        for each in stats:
            if 'reputation' in each['href']:
                reputation = each.text
            elif 'vouches' in each['href']:
                vouches = each.text
        likes = soup.find('strong', style=lambda value: value and 'font-size: 17px;' in value and 'font-weight: 600 !important;' in value).text
        online = soup.find('strong', style=lambda value: value and 'margin-left: auto;' in value).text

        return username, cred, reputation, vouches, likes, online

    def update_my_key(self) -> str:
        endpoint = 'usercp.php'
        response = self.session.get(self.main_url + endpoint).text
        soup = BeautifulSoup(response, 'html.parser')
        my_key = soup.find('input', attrs={'type': 'hidden', 'name': 'my_post_key'}).get('value')
        print(f"Updated the post key: {my_key}")
        return my_key

    def get_credentials(self) -> str:
        endpoint = 'usercp.php'
        response = self.session.get(self.main_url + endpoint).text
        soup = BeautifulSoup(response, 'html.parser')
        email = soup.find('strong', text="Email:").next_sibling.strip()
        reg_date = soup.find('strong', text="Registration Date:").next_sibling.strip()
        group = soup.find('strong', text="Primary Group:").next_sibling.strip()
        return email, reg_date, group

    def get_recent_threads(self) -> None:
        endpoint = 'usercp.php'
        soup = BeautifulSoup(self.session.get(self.main_url + endpoint).text, "html.parser")
        threads = soup.find_all('td', class_='col_row responsivehide td-rounded')
        print("Parsing the recent threads...")
        for thread in threads:
            date = thread.find('span', title=lambda value: value and '2020' in value)
            if date == None:
                date = "A long time ago"
            else:
                thread_url = self.session.get(f"{self.main_url}/{thread.a['href']}").url # to avoid getting logged out after sending the request (will implement http/2.0 header support later to clean up the code)
                soup = BeautifulSoup(self.session.get(thread_url).text, "html.parser")
                try:
                    thread_id = soup.find('input', attrs={'type': 'hidden', 'name': 'tid'}).get('value')
                except:
                    print(thread_url)
                    time.sleep(15)
                    continue
                self.cached_threads[thread_id] = date.text    

    def check_login(self) -> None:
        print("Trying to login...\n")
        email, reg_date, group = self.get_credentials()
        username, cred, reputation, vouches, likes, online = self.get_info()
        print(f"Logged in as {username}\nEmail address: {email}\nRegistration date: {reg_date}\nUser group: {group}\nReputation: {reputation}\nVouches: {vouches}\nLikes: {likes}\nCredits: {cred}\nCurrent online: {online}")

    def check_threads(self) -> None:
        dates = ('hour', 'Today', 'Yesterday')
        while True:
            self._my_post_key = self.update_my_key()
            self.get_recent_threads()
            for thread, thread_date in self.cached_threads.items():
                if any(i in thread_date for i in dates):
                    self.bump_thread(thread)
                    print(f"Successfully autobumped the thread {thread}")
                    time.sleep(14)
            print("All of the threads have been autobumped\n")
            time.sleep(3650)

    def bump_thread(self, tid) -> None:
        endpoint = 'newreply.php?ajax=1'
        phrases = ['Bumping this', 'Bumping this thread', 'Bumping this topic']
        dots = "".join('.' for _ in range(randint(1,10)))
        random_phrase = choice(phrases) + dots
        data = {'my_post_key': self._my_post_key,
        'action': 'do_newreply',
        'tid': tid,
        'method': 'quickreply',
        'message': random_phrase,
        'postoptions[signature]': '1'}
        self.session.post(self.main_url + endpoint, data=data).json()

OGUAutobumper().check_threads()