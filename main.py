import discord
from discord.ext.tasks import loop
import datetime
import os
from keep_alive import keep_alive

client = discord.Client()
countdowns = {}

helpMessage = [
        "***Dead Man's Switch***",
        ""
        "",
        "To see this message:",
        "`dms help`",
        "",
        "To set a countdown:",
        "`dms set [@username] [time]`",
        "",
        "Available time formats:",
        "`s - second",
        "m - minute",
        "h - hour",
        "d - days",
        "m - month",
        "y - year`",
        "",
        "Example:",
        "`dms set @Mr. Whimsi 5d`",
        "",
        "To check a user's countdown:",
        "`dms check [@username]`",
        "",
        "To delete a user's countdown:",
        "`dms delete [@username]`",
        "",
        "**A countdown will reset if the user types a message.**",
        "**Otherwise the user will be pronounced dead.**",
    ]

@client.event
async def on_ready():
    print(f'Initializing {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    mention = f'<@!{message.author.id}>'

    if mention in countdowns:
        delta = countdowns[mention][1]
        newDue = datetime.datetime.now() + delta

        countdowns[mention] = [newDue, delta, message]
        await message.channel.send(f'{mention} is not dead! Countdown has been reset until {newDue}')

        countdowns[mention] = [newDue, delta, message]


    if message.content.startswith('dms help'):
        await message.channel.send('\n'.join(helpMessage))

    elif message.content.startswith('dms set'):
        try:
            deadMan, length = message.content[7:].strip().split()
        except:
            await message.channel.send('I did not understand. Try again.\n\n' + '\n'.join(helpMessage))
            pass

        # create countdown
        if not deadMan in countdowns:

            if len(length) < 2:
                await message.channel.send('I did not understand. Try again.\n\n' + '\n'.join(helpMessage))

            try:
                n = int(length[:-1])
                t = length[-1]
            except:
                await message.channel.send('I did not understand. Try again.\n\n' + '\n'.join(helpMessage))

            if t == 's':
                delta = datetime.timedelta(seconds=n)
            elif t == 'm':
                delta = datetime.timedelta(minutes=n)
            elif t == 'h':
                delta = datetime.timedelta(hours=n)
            elif t == 'd':
                delta = datetime.timedelta(days=n)
            elif t == 'm':
                delta = datetime.timedelta(months=n)
            elif t == 'y':
                delta = datetime.timedelta(years=n)

            dueTime = datetime.datetime.now() + delta

            countdowns[deadMan] = [dueTime, delta, message]

            await message.channel.send(f'Countdown set for {deadMan} every {length}')
        else:
            await message.channel.send(f'{deadMan} already has a countdown!')

    elif message.content.startswith('dms check') and '@' in message.content:
        user = message.content[10:].strip()

        if user in countdowns:
            await message.channel.send(f"{user} has until {countdowns[user][0]} to respond.")
        else:
            await message.channel.send(f"{user} doesn't have a countdown!")

    elif message.content.startswith('dms delete') and '@' in message.content:
        user = message.content[11:].strip()

        if user in countdowns:
            del countdowns[user]
            await message.channel.send(f"{user}'s countdown has been deleted.")
        else:
            await message.channel.send(f"{user} doesn't have a countdown!")

    else:
        if 'dms' in message.content:
            await message.channel.send('\n'.join(helpMessage))


@loop(seconds=1)
async def countdown():
    toRemove = []
    for c in countdowns:
        message = countdowns[c][2]
        currentTime = datetime.datetime.now()
        if countdowns[c][0] <= currentTime:
            toRemove.append(c)
            await message.channel.send(f'{c} has not been active for {countdowns[c][1]}. {c} is probably dead.')

    for r in toRemove:
        del countdowns[r]

token = os.environ['token']

keep_alive()
countdown.start()
client.run(token)