import discord
import time
import random
import os

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True

client = discord.Client(intents=intents)
usernames = []

TOKEN = os.getenv("DISCORD_TOKEN")

# Add users with errors to blacklist so that we don't keep making API calls to change these users.
memberBlacklist = []

file = open('usernames.txt', 'r')
for line in file:
    usernames.append(line[:-1])


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    while True:
        users = client.get_all_members()
        for member in users:
            if member.display_name not in memberBlacklist:
                await changeNick(member)
            else:
                print('Not modifying ' + member.display_name + ', as we didn\'t have permission to last time.')
        time.sleep(5)


def generateusername():
    newUsername = ""
    usernameSeed = usernames[random.randint(0, len(usernames))]

    # Determine where numbers occur
    # 0 = None; 1 = Before; 2 = After; 3 = Both
    randomInt = random.randint(0, 3)
    if randomInt == 0:
        newUsername += usernameSeed
    if randomInt == 1:
        for i in range(0, random.randrange(0, 6)):
            newUsername += str(random.randrange(0, 9))
        newUsername += usernameSeed
    if randomInt == 2:
        newUsername += usernameSeed
        for i in range(0, random.randrange(0, 6)):
            newUsername += str(random.randrange(0, 9))
    if randomInt == 3:
        for i in range(0, random.randrange(0, 6)):
            newUsername += str(random.randrange(0, 9))
        newUsername += usernameSeed
        for i in range(0, random.randrange(0, 6)):
            newUsername += str(random.randrange(0, 9))
    return newUsername


async def changeNick(member):
    print("Changing nickname for " + member.display_name)
    newname = generateusername()
    try:
        await member.edit(nick=newname)
    except:
        print('    Couldn\'t edit member ' + member.display_name)
        print('    Adding member to blacklist...')
        memberBlacklist.append(member.display_name)

    print("    Changed username to " + newname)

client.run(TOKEN)
