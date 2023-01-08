import os
import time
import asyncio
import discord
import subprocess
import pandas as pd
import datetime
from discord import channel
from discord.ext import tasks
from dotenv import load_dotenv
from discord.ext import commands
from discord_components import (
    Button,
    ButtonStyle,
    Select,
    SelectOption,
    ComponentsBot
)
from table2ascii import table2ascii as t2a, PresetStyle

load_dotenv()
bot = ComponentsBot('!')
country = {
    'England': 'England',
    'Germany': 'Germany',
    'Italy': 'Italy',
    'France': 'France',
    'Spain': 'Spain',
    'Netherlands': 'Netherlands',
    'Portugal': 'Portugal',
    'Turkey': 'Turkey',
    'Belgium': 'Belgium',
    'United States': 'United States',
    'Scotland': 'Scotland',
    'China': 'China', }
ids = []


def back_button() -> list[Button]:
    ''' Back button and Done button'''
    back_button = [[Button(label='Back', custom_id='Back', style=4), Button(label='Done', custom_id='Done', style=3)],
                   Button(label='Main menu', custom_id='main', style=3)]
    return back_button


def country_menu() -> list[Select]:
    coursemenu = [
        Select(
            placeholder="Select a country",
            options=[
                SelectOption(label=i, value=i) for i in set(country)]
        )
    ]
    return coursemenu


def get_matches(sort_by_time: bool = False, sort_by_league: bool = False, today: bool = False, tomorrow: bool = False):
    if today == True:
        day_chosen = datetime.date.today().strftime("%Y-%m-%d")
    if tomorrow == True:
        day_chosen = datetime.date.today() + datetime.timedelta(days=1)
        day_chosen = day_chosen.strftime("%Y-%m-%d")
    columns = ['Date', 'Time', 'HomeTeam', 'AwayTeam', 'B365H', 'B365D', 'B365A']
    all_fixtures = pd.read_csv('/users/USER/desktop/Data sci/fixtures.csv', encoding='cp1252')
    all_fixtures = all_fixtures[columns]
    all_fixtures['Date'] = pd.to_datetime(all_fixtures['Date'])
    todays_matches = all_fixtures[all_fixtures['Date'] == day_chosen]
    if sort_by_time == True:
        todays_matches.sort_values(by=['Time'], inplace=True)
    todays_matches.to_csv('todays_matches.csv', index=False)
    todays_matches = return_list('todays_matches.csv')
    return todays_matches


def today_menu() -> list[list[Button]]:
    menu = [[
        Button(label='Todays odds(bet365)', custom_id='today'),
        Button(label='Tomorrow', custom_id='tomorrow'),
        Button(label="Today's prediction", custom_id='today_pred')
    ]]
    return menu


def league_menu(country: str) -> list[Select]:
    PATH = f'/users/USER/desktop/Data sci/{country}/'
    leagues = os.listdir(PATH)
    leaguemenu = [
        Select(
            placeholder="Select a league",
            options=[
                SelectOption(label=i, value=i) for i in leagues
            ]
        )
    ]
    return leaguemenu


def admin_menu():
    adminmenu = [Button(label='Get fixtures', custom_id='fixtures', style=3),
                 [Button(label='Run all', custom_id='all', style=3),
                  Button(label='league options', custom_id='options', style=3)]
                 ]
    return adminmenu


def match_embeds(twod_list: list[list]) -> discord.Embed:
    embed = discord.Embed(title=f"__**Today's matches with B365 odds:**__", color=0x03f8fc)
    for m in twod_list:
        date = m[0]
        hour = int(m[1].split(":")[0]) - 5
        minute = m[1].split(":")[1]
        time = f'{hour}:{minute}'
        hodds = m[4]
        dodds = m[5]
        aodds = m[6]
        embed.add_field(name=f'**{m[2]} - {m[3]}**',
                        value=f'> Date: {date}\n> Time: {time}\n> 1: {hodds}\n> X: {dodds}\n> 2: {aodds}', inline=False)
    return embed


def return_list(csv_file: str) -> list[list]:
    '''Returns a 2-d list consisting of the rows of the CSV file as the inner list'''
    dataframe = []
    with open(csv_file, 'r') as f:
        data = f.readlines()
        for i, line in enumerate(data):
            if i == 0:  # Skipping the first line/row
                continue
            line = line.rstrip('\n')
            line = line.split(',')
            dataframe.append(line)
    return dataframe


@bot.event
async def on_ready():
    channel = bot.get_channel(900489176342986764)
    await channel.send('loading.')


@bot.event
async def on_message(message):
    msg = message.content
    if msg == "hello":
        await message.channel.send("pies are better than cakes. change my mind.")
    await bot.process_commands(message)


@bot.command()
async def predictions(ctx):
    await ctx.send('Select a country to view the league', components=[country_menu()])


@bot.command()
async def matches(ctx):
    await ctx.send('View bets/matches', components=today_menu())


@bot.event
async def on_select_option(interaction):
    print(interaction.values)
    if len(interaction.values) > 1:  # Multiple selections
        for og in interaction.values:
            value = og.lower()
            value = value.split()
            if len(value) > 1:
                value = '_'.join(value)
            else:
                value = value[0]
            for count in country:
                try:
                    if og in os.listdir(f'/users/USER/desktop/Data sci/{count}/'):
                        league_prediction = subprocess.Popen(
                            ['C:\\Users\\USER\\AppData\\Local\\Programs\\Python\\Python39\\python.exe',
                             f'/users/USER/desktop/Data sci/{count}/{og}/{value}.ipynb'])
                        print('Running...')
                        league_prediction.wait()
                except Exception as e:
                    print(count, og, value)
                    print(e)
    elif interaction.values[0] not in country:
        league_selected = interaction.values[0]
        league = league_selected.lower()
        league = league.split()
        if len(league) > 1:
            league = '_'.join(league)
        else:
            league = league[0]
        # Getting predictions for chosen league
        PATH = '/users/USER/desktop/Data sci/model predictions/'
        prediction = return_list(f'{PATH}{league}.csv')
        embed = discord.Embed(title=f"__**{league} predictions:**__", color=0x03f8fc)
        for p in prediction:
            date = p[0]
            time = p[1]
            hodds = p[4]
            dodds = p[5]
            aodds = p[6]
            embed.add_field(name=f'**{p[2]} - {p[3]}**',
                            value=f'> Date: {date}\n> Time: {time}\n> 1: {hodds}\n> X: {dodds}\n> 2: {aodds}',
                            inline=False)
        await interaction.send(embed=embed)
    else:
        # Getting leagues based on countries selected
        country_selected = interaction.values[0]
        await interaction.respond(content=f"{country_selected} selected!", components=league_menu(country_selected))


@bot.event
async def on_button_click(interaction):
    custom_id = interaction.custom_id
    if custom_id == "fixtures":
        pass
    if custom_id == "today" or custom_id == "tomorrow":
        if custom_id == "today":
            matches = get_matches(today=True)
        else:
            matches = get_matches(tomorrow=True)
        ids.append(custom_id)
        embed = match_embeds(matches)
        print(len(embed))
        await interaction.send(embed=embed, components=[Button(label='Sort by', custom_id='sort')])
    if custom_id == "today_pred":
        pass
    if custom_id == "sort":
        # sort by league or Time
        await interaction.send('How would you like to sort the matches', components=[
            [Button(label='By time', custom_id='time'), Button(label='By league', custom_id='by_league')],
            Button(label='Both', custom_id='league_time')])
    if custom_id == "time":
        if ids[-1] == 'today':
            matches = get_matches(sort_by_time=True, today=True)
        if ids[-1] == 'tomorrow':
            matches = get_matches(sort_by_time=True, tomorrow=True)
        embed = match_embeds(matches)
        await interaction.send(embed=embed)
    if custom_id == "bets":
        pass
    if custom_id == "all":
        pass
    if custom_id == "by_league":
        pass
    if custom_id == "options":
        all_leagues = []
        for count in country:
            PATH = f'/users/USER/desktop/Data sci/{count}/'
            leagues = os.listdir(PATH)
            for league in leagues:
                all_leagues.append(league)
        select_leagues = [Select(
            options=[SelectOption(label=i, value=i) for i in all_leagues],
            placeholder="Choose one or more leagues",
            min_values=1,  # the minimum number of options a user must select
            max_values=5  # the maximum number of options a user can select
        )]
        await interaction.send('Choose the leagues to run', components=select_leagues)


@bot.command()
async def test(ctx, *args):
    await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))


@commands.is_owner()  # make sure no one else uses it
@bot.command()
async def admin(ctx):
    await ctx.send('What would you like to do?', components=admin_menu())


@bot.command()
async def clear(ctx):
    await ctx.channel.purge()


while True:
    bot.run(os.getenv('D_TOKEN'))
    time.sleep(1)
