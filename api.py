import os
from dotenv import load_dotenv
import requests

load_dotenv()
bearer = os.getenv("COC_API_KEY")
clanTag = os.getenv("CLAN_TAG")

base = "https://api.clashofclans.com/v1"
headers = {
        "Authorization": "Bearer " + str(bearer),
        "Accept": "application/json"
    }

def fetch(route):
    return requests.get(route, headers=headers)

def parseTag(tag):
    if '#' in tag:
        tag = tag.replace('#', '')
    return '%23'+tag

def verify_player_tag(tag):
    api_url = base + '/players/' + parseTag(tag)
    response = fetch(api_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return False

def get_current_war_info():
    api_url = base + '/clans/' + parseTag(clanTag) + '/currentwar'
    response = fetch(api_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return False

def get_clan_info():
    api_url = base + '/clans/' + parseTag(clanTag)
    response = fetch(api_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return False