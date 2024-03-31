import discord
import json 
import schedule
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

import api
import utils

from const import DELTA_CRON_WAR
import messages 

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la variable TOKEN
token = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Dictionnaire des commandes et leurs descriptions
commandes = {
    "!add <tag>": messages.HELP["ADD"],
    "!remove":messages.HELP["REMOVE"],
    "!clan": messages.HELP["CLAN"],
    "!war": messages.HELP["WAR"]
}

# Charge les données du fichier JSON (si le fichier existe déjà)
try:
    with open('data.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    data = {}

async def help(message):
    text = messages.HELP["TITLE"]
    text = text + "\n".join([f"- {commande}: {description}" for commande, description in commandes.items()])
    await message.channel.send(text)
    

def save_tag(tag):
     # Sauvegarde les données dans le fichier JSON
        with open('data.json', 'w') as f:
            json.dump(tag, f)

async def add_tag(message):
    # Vérifie si un tag est fourni
        if len(message.content.split()) < 2:
            await message.channel.send(messages.HELP["ADD_WRONG"])
            return
        
        # Récupère le tag fourni par l'utilisateur
        tag = message.content.split()[1]
        player = api.verify_player_tag(tag)

        if player == False:
            await message.channel.send(messages.TAG['NO_PLAYER_FOUND'](message.author.mention, tag))
        else:
            data[str(message.author.id)] = tag
            save_tag(data)
            await message.channel.send(message.TAG['SUCCESS'](message.author.mention, player))   

async def remove_tag(message):
     # Vérifie si l'utilisateur a déjà un tag enregistré
        if str(message.author.id) not in data:
            await message.channel.send(messages.TAG['NO_TAG_FOUND'](message.author.mention))
            return
        
        # Supprime le tag associé à l'identifiant de l'utilisateur dans le fichier JSON
        del data[str(message.author.id)]
        
        # Sauvegarde les données dans le fichier JSON
        with open('data.json', 'w') as f:
            json.dump(data, f)
        
        await message.channel.send(messages.TAG['TAG_REMOVED'](message.author.mention))

async def get_war_info(message):
    infos = api.get_current_war_info() 
    if infos['state'].upper() == 'NOT_IN_WAR':
        infoStatus = messages.WAR['STATUS_NOT_IN_WAR']
    elif infos['state'] == "warEnded":
        # TODO : Dire si on a gagné ou pas
        infoStatus = messages.WAR['STATUS_ENDED']
    elif infos['state'].upper() == 'IN_MATCHMAKING':
        infoStatus = messages.WAR[infos['state'].upper()]
    elif infos['state'].upper() == 'WAR' or infos['state'].upper() == 'INWAR':
        opponent = infos['opponent']
        starsDiff = infos['clan']['stars'] - opponent['stars']
        if starsDiff > 0:
            status = f'Nous menons la guerre de {abs(starsDiff)} :star:'
        elif starsDiff == 0:
            purcentDiff = infos['clan']['destructionPercentage'] - opponent['destructionPercentage']
            if purcentDiff > 0:
                status = f"Égalité aux :star:, mais nous menons de {purcentDiff}% de destruction"
            else:
                status = f"Égalité aux :star:, mais nous sommes mené de {purcentDiff}% de destruction"
        else:
            status = f'Nous sommes mené de {abs(starsDiff)} :star:'
        infoStatus = f'''
        Nous sommes en guerre contre **{opponent['name']}**.
        {status}
        **Oradon Froster** : {infos['clan']['stars']} :star: en {infos['clan']['attacks']} :crossed_swords: pour {infos['clan']['destructionPercentage']}% de destruction
        **{opponent['name']}** : {opponent['stars']} :star: en {opponent['attacks']} :crossed_swords: pour {opponent['destructionPercentage']}% de destruction
        ''' 
    
    elif infos['state'].upper() == 'PREPARATION':
       opponent = infos['opponent']
       timeLeft = utils.getTimeLeft(infos['startTime'])
       infoStatus = f"En préparation de {str(infos['teamSize'])}VS{str(infos['teamSize'])} contre **{opponent['name']}**. Il reste **{timeLeft}** avant la bagarre !"
    else:
        infoStatus = "Aucune idée " + infos['state']
    await message.channel.send(infoStatus)

async def get_clan_info(message):
    clan = api.get_clan_info()
    sum_town_hall_level = 0
    sum_trophies = 0
    for member in clan['memberList']:
        sum_town_hall_level += member['townHallLevel']
        sum_trophies += member['trophies']
    avg_town_hall_level = round(sum_town_hall_level / len(clan['memberList']), 2)
    avg_trophies = round(sum_trophies / len(clan['memberList']), 2)
    text = f'''
    **{clan['name']}** - Le clan est niveau **{clan['clanLevel']}** et comporte **{clan['members']}** membres.
    - Winrate en guerre de clan : {round(clan['warWins'] / (clan['warWins'] + clan['warLosses']) * 100)}% ({clan['warWins']}/{clan['warLosses']})
    \n- Hôtel de ville moyen : {avg_town_hall_level}
    \n- Trophées moyen par membres : {avg_trophies}
    '''
    await message.channel.send(text)    

async def trigger_cron():
    await checkMembersAttacks()
                                           
async def checkMembersAttacks():
    infos = api.get_current_war_info()
    date = datetime.strptime(infos['endTime'], "%Y%m%dT%H%M%S.%fZ")
    if date < datetime.now() + timedelta(hours=DELTA_CRON_WAR):
        print(f"La guerre est dans moins de {DELTA_CRON_WAR}h")
        # Charger le contenu du fichier JSON
    with open("data.json", "r") as file:
        data = json.load(file)
    if infos['state'].upper() == 'WAR' or infos['state'].upper() == 'INWAR':
        members = infos['clan']['members']
        for user_id, tag in data.items():
            for member in members: 
                if '#'+tag == member['tag']:
                    if 'attacks' not in member or len(member['attacks']) < 2 :
                        opponents = infos['opponent']['members']
                        target = [opp for opp in opponents if opp['mapPosition'] == member['mapPosition']][0]   
                        if target['opponentAttacks'] > 0:
                            target = [opp for opp in opponents if int(opp['mapPosition']) == int(member['mapPosition'])-1][0]
                        # TODO: Recursive shit
                        if target :
                            # Direct opponent found, and nobody attack him
                            await send_channel_message(f"<@{user_id}> Mec, t'as pas fait toutes tes attaques, déboîte le **{target['mapPosition']} - {target['name']}** tout de suite")
    else: 
        print(f'La guerre est dans plus de {DELTA_CRON_WAR}h')

channel_id = os.getenv("CHANNEL_ID")
async def send_channel_message(message_content):
    channel = client.get_channel(int(channel_id))
    print(channel)
    if channel:
        await channel.send(message_content)
    else:
        print(f"Impossible de trouver le canal avec l'ID {channel_id}")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    # Si c'est un message du bot
    if message.author == client.user:
        return

    if message.content.startswith('!help'):
        await help(message)
        return

    if message.content.startswith('!add'):
        await add_tag(message)
        return
        
    elif message.content.startswith('!remove'):                
        await remove_tag(message)
        return

    elif message.content.startswith('!war'):                
        await get_war_info(message)
        return

    elif message.content.startswith('!clan'):                
        await get_clan_info(message)
        return
    
    elif message.content.startswith('!cron'):
        await trigger_cron()
        return

    else:
        await message.channel.send(f"Mais frérot arrête tes conneries, utilise !help et me casse pas les couilles")
        return


# CRON player reminder
# schedule.every().hour.do(players_reminder)

client.run(token)