import discord
from discord.ext import commands, tasks
import random
import requests
import re


# Main looper
class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = []
        self.looper.start()
        self.running = True
        self.memberBlacklist = []

        self.usernames = []
        r = requests.get('https://asf.randomcpu.com/usernames.txt', allow_redirects=True)
        with open('usernames.txt', 'wb') as f:
            f.write(r.content)
        file = open('usernames.txt', 'r')
        for line in file:
            self.usernames.append(line[:-1])

    def cog_unload(self):
        self.looper.cancel()

    # Setup custom commands
    @commands.command()
    async def stop(self, ctx):
        """Stops running the name changing service"""
        if self.running:
            self.running = False
            await ctx.send("Stopped!")
        else:
            await ctx.send("Bot already stopped, no status change.")

    @commands.command()
    async def resetnames(self, ctx):
        """Reset all names to default and pauses bot"""
        if self.running:
            self.running = False
            await ctx.send("Stopped name changing service!")
        await self.changeNamesDefault()
        await ctx.send("Root names deleted!")

    @commands.command()
    async def clearwords(self, ctx):
        """Deletes all root names from the list and pauses bot"""
        if self.running:
            self.running = False
            await ctx.send("Stopped name changing service!")
        self.usernames = []
        await ctx.send("Root names deleted!")

    @commands.command()
    async def addword(self, ctx, wordOrURL):
        """Adds a root name to the list\n
        Usage: addword [WORD]\n
               addword [URL of text file]"""
        # Check if the string is a URL
        if re.match(r"https?://", wordOrURL):
            print("wordOrURL " + wordOrURL + " is a URL!")
            r = requests.get(wordOrURL, allow_redirects=True)
            with open('usernames.txt', 'wb') as f:
                f.write(r.content)
            file = open('usernames.txt', 'r')
            for line in file:
                self.usernames.append(line[:-1])
        else:
            self.usernames.append(wordOrURL)
        await ctx.send("Root names added!")
    @addword.error
    async def addword_error(self, ctx, error):
        await ctx.send("Please specify a word or URL as a parameter!")

    @commands.command()
    async def delword(self, ctx, word):
        """Removes a root word from the list"""
        self.usernames.remove(word)
        await ctx.send("Removed " + word + " from root usernames!")
    @delword.error
    async def delword_error(self, ctx, error):
        await ctx.send("Please specify a word as a parameter!")

    @commands.command()
    async def start(self, ctx):
        """Starts running the name changing service"""
        if not self.running:
            self.running = True
            await ctx.send("Started!")
        else:
            await ctx.send("Bot already started, no status change.")

    @commands.command()
    async def listwords(self, ctx):
        """Returns a full list of root username values"""

        # Dump usernames to file

        # Setup file for attachment
        file = discord.File("usernames.txt")

        await ctx.send("Here's the full list of root usernames!", file=file)

    #@commands.command()
    #async def mentioneveryone(self, ctx):
    #    """Mentions everyone in server"""
    #
    #    users = self.bot.get_all_members()
    #    message = ""
    #    for user in users:
    #        message += user.mention + " "
    #
    #    channel = await self.bot.fetch_channel(617596739368517633)
    #    await channel.send(message)

    # Custom functions
    async def changeNamesRandom(self):
        """
        Changes all users to a random name.
        :return: 0
        """
        # Pause if there are no words in wordlist
        if len(self.usernames) == 0:
            self.running = False
            return 1
        else:
            users = self.bot.get_all_members()
            for member in users:
                if self.running:
                    if member.display_name not in self.memberBlacklist:
                        await self.changeNick(member)
                    else:
                        print('Not modifying ' + member.display_name + ', as we didn\'t have permission to last time.')
            return 0

    async def changeNamesDefault(self):
        """
        Changes all users to default name
        :return: 0
        """
        users = self.bot.get_all_members()
        for member in users:
            if member.display_name not in self.memberBlacklist:
                try:
                    await member.edit(nick=member.name)
                except:
                    print('    Couldn\'t edit member ' + member.name)
                    print('    Adding member to blacklist...')
                    self.memberBlacklist.append(member.display_name)
            else:
                print('Not modifying ' + member.name + ', as we didn\'t have permission to last time.')

    async def changeNick(self, member):
        """
        Changes given member's nickname to a random one
        :param member: Member struct to change to random nickname
        :return: `0` if success; `1` for failure
        """
        print("Changing nickname for " + member.name)
        newName = self.generateusername()
        try:
            await member.edit(nick=newName)
        except:
            print('    Couldn\'t edit member ' + member.name)
            print('    Adding member to blacklist...')
            self.memberBlacklist.append(member.name)
            return 1
        return 0

    def generateusername(self):
        """
        Returns a randomized username
        :return: Randomized username string
        """
        newUsername = ""
        if self.running:
            usernameSeed = self.usernames[random.randint(0, len(self.usernames))]

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

    # Main Loop
    @tasks.loop(seconds=15)
    async def looper(self):
        if self.running:
            await self.changeNamesRandom()

    @looper.before_loop
    async def before_looper(self):
        print('Waiting for discord.py to be ready...')
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(MyCog(bot))
