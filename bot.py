# bot.py
import os, json
import pygsheets
import discord
from discord.ext import commands
import pandas as pd
import numpy as np
from dotenv import load_dotenv

CARD_ID = ""

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = 'karuta-cards'



gc = pygsheets.authorize(service_account_env_var = 'GOOGLE_JSON')
wks = gc.open('Karuta storage')[0]

all_data = wks.get_all_records()

records_df = pd.DataFrame.from_dict(all_data)



#authorization

def convertStartToTerms(starString):
    stars = ["★★★★", "★★★☆", "★★☆☆", "★☆☆☆", "☆☆☆☆"]
    terms = ["Mint", "Excellent", "Good", "Poor", "Badly Damaged"]

    return terms[stars.index(starString)]


#parse kc embeded description
def parseKCAll(description):
    cards = []
    # print(description.encode('unicode_escape'))

    cardsArr = description.split("**\n")

    for card in cardsArr:
        separated = card.split("**")
        cardId = separated[1].split("`")[1]
        backwards = 1
        if(separated[len(separated)-1] == ''):
            backwards = 2
        cardName = separated[len(separated)-backwards]
        cardSeries = separated[2].split("·")[4]
        cardCondition = separated[2].split("·")[1].split("`")[1]

        cards.append({"Id": cardId, "Name": cardName, "Series": cardSeries, "Condition": convertStartToTerms(cardCondition)})
    return cards   

#parse kc embeded description
def parseKC(description):
    cards = []
    # print(description.encode('unicode_escape'))

    cardsArr = description.split("**\n")

    for card in cardsArr:
        separated = card.split("**")
        cardId = separated[1].split("`")[1]
        backwards = 1
        if(separated[len(separated)-1] == ''):
            backwards = 2
        cardName = separated[len(separated)-backwards]
        cardSeries = separated[2].split("·")[4]
        cardCondition = separated[2].split("·")[1].split("`")[1]

        cards.append({"Id": cardId, "Name": cardName, "Series": cardSeries, "Condition": convertStartToTerms(cardCondition)})
        return cards    

def parseLU(desciption):
    cardArr = desciption.split("**\n")

    cardWish = cardArr[2].split("· **")[-1]
    cardClaimrate = cardArr[8].split("· **")[-1]
    cardTotal = cardArr[4].split("· **")[-1]
    cardEdition = cardArr[3].split("· **")[-1]

    return {"Edition": cardEdition, "Claimrate": cardClaimrate, "Total Generated": cardTotal, "Wishlisted":  cardWish}

def searchWorkStats(string, attributeArr):
    for attribute in attributeArr:
        if(attribute in string):
            return (attribute, string.split(" ")[0])

def parseWI(desciption):
    cardInfo = {}
    cardArr = desciption.split("**\n")
    cardEffort = cardArr[1].split("· **")[-1]
    rest = cardArr[2].split("js")[1].split("\n")
    for item in rest:
        if (len(item )> 4):
            (attrbute, value) = searchWorkStats(item, ["Base value", "Wellness", "Purity", "Grabber", "Dropper", "Quickness", "Style", "Toughness", "Vanity"])
            cardInfo[attrbute] = value
    cardInfo["Effort"] = cardEffort
    return cardInfo
    

def getRowbyId(cardId, sheet):
    maximum = sheet["Id"].shape
    for i in range(0, maximum[0]):
        if(sheet.loc[i, "Id"] == cardId):
            row = i+2
            return row
    return getLastRow(sheet)

def getLastRow(sheet): 
    maximum = sheet["Id"].shape
    return maximum[0] + 2

def getCellByIdAndType(cardId, attributeType, sheet):
    row = getRowbyId(cardId, sheet)
    col = sheet.columns.get_loc(attributeType)

    return (row, col+1)


def updateSheet(cardId, attributeType, attributeValue, sheetCache, sheet):
    row = getRowbyId(cardId, sheetCache)
    location = getCellByIdAndType(cardId, attributeType, sheetCache)

    sheet.cell(location).set_value(attributeValue)
    sheetCache.loc[row-2, attributeType] = attributeValue


bot = commands.Bot(command_prefix='zop ')

@bot.command(name='lu')
@commands.has_role('admin')
async def look_up(ctx, cardId = ""):
    if(len(cardId) > 0):
        global CARD_ID
        CARD_ID = cardId
    else:
        cardId = CARD_ID
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=CHANNEL)
    messages = await existing_channel.history(limit=2).flatten()

    for message in messages:
        for embed in message.embeds:
            await ctx.send('Parsing look up')
            info = parseLU(embed.description)
            for item in info:
                updateSheet(cardId, item, info[item], records_df, wks)
    await ctx.send('Done updating the spreadsheet')

@bot.command(name='kcall')
@commands.has_role('admin')
async def look_up_cards_all(ctx):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=CHANNEL)
    messages = await existing_channel.history(limit=2).flatten()

    for message in messages:
        for embed in message.embeds:
            cards = parseKCAll(embed.description)
            await ctx.send('Dumping Cards')
            for card in cards:

                updateSheet(card["Id"], "Id", card["Id"], records_df, wks)
                updateSheet(card["Id"], "Name", card["Name"],records_df, wks)
                updateSheet(card["Id"], "Series", card["Series"],records_df, wks)
                updateSheet(card["Id"], "Condition", card["Condition"],records_df, wks)
    await ctx.send('Done')

            
@bot.command(name='wi')
@commands.has_role('admin')
async def look_up_work(ctx, cardId = ""):
    if(len(cardId) > 0):
        global CARD_ID
        CARD_ID = cardId
    else:
        cardId = CARD_ID
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=CHANNEL)
    messages = await existing_channel.history(limit=2).flatten()
    for message in messages:
        for embed in message.embeds:
            await ctx.send('Parsing work stats')
            info = parseWI(embed.description)
            name = embed.description.split("**\n")[0].split("· **")[-1]
            info["Photo"] = '=IMAGE(\"'+embed.thumbnail.url+'\")'
            for item in info:
                updateSheet(cardId, item, info[item], records_df, wks)
    await ctx.send('Done updating spreadsheet!\n **klu '+name+'** \nzop lu\nshould finsih updating the spreadsheet!')

@bot.command(name='kc')
@commands.has_role('admin')
async def look_up_most_recent(ctx):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=CHANNEL)
    messages = await existing_channel.history(limit=2).flatten()
    for message in messages:
        for embed in message.embeds:
            await ctx.send('Parsing karuta collection')
            info = parseKC(embed.description)[0]
            
            updateSheet(info["Id"], "Id", info["Id"], records_df, wks)
            updateSheet(info["Id"], "Name", info["Name"],records_df, wks)
            updateSheet(info["Id"], "Series", info["Series"],records_df, wks)
            updateSheet(info["Id"], "Condition", info["Condition"],records_df, wks)
            global CARD_ID 
            CARD_ID = info["Id"]
    await ctx.send('Done updating card **' +CARD_ID+'** in the spreadsheet\n**kwi '+CARD_ID+'** \nzop wi\nshould be entered further update your spreadsheet')

@bot.command(name='sb')
@commands.has_role('admin')
async def look_up_most_recent(ctx):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=CHANNEL)
    messages = await existing_channel.history(limit=2).flatten()
    for message in messages:
        for embed in message.embeds:
            cards = parseKCAll(embed.description)
            await ctx.send('Deleting Cards')
            print(len(cards))
            for card in cards:
                try:
                    row = getRowbyId(card["Id"], records_df)
                    print(row)
                    print(records_df["Id"].shape)
                    wks.delete_rows(row, number=1)
                    print(records_df.loc[[row-2]])
                    records_df.drop(index=row-2, inplace=True)
                    print("deleting row", row-2)
                    records_df.reset_index(drop=True, inplace=True)
                    print(records_df["Id"].shape)
                except:
                    pass

    await ctx.send('Done deleting cards from spreadsheet')


bot.run(TOKEN)

