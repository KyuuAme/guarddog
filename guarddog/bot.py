from discord.ext import commands

from guarddog.config import config

if config.getboolean('Server', 'DevMode', fallback=False):
    bot = commands.Bot(command_prefix=['dd!'], case_insensitive=True)
else:
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('d!'), case_insensitive=True)
