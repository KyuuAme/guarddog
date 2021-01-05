import math
import traceback

import discord
from discord.ext import commands
from loguru import logger

from guarddog.bot import bot
from guarddog.config import config

# bot.add_cog(Community(bot, config))


@bot.event
async def on_ready():
    logger.debug(f"Logged in as {bot.user.name} ({bot.user.id})")
    logger.success('Shizuku is on the prowl!')


# noinspection DuplicatedCode
@bot.event
async def on_command_error(ctx: commands.context.Context, error: Exception):
    # if command has local error handler, return
    if hasattr(ctx.command, 'on_error'):
        return

    # get the original exception
    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.BotMissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
        if len(missing) > 2:
            fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
        await ctx.send(_message)
        return

    if isinstance(error, commands.DisabledCommand):
        await ctx.send('This command has been disabled.')
        return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after)))
        return

    if isinstance(error, commands.MissingPermissions):
        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
        if len(missing) > 2:
            fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        _message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
        await ctx.send(_message)
        return

    if isinstance(error, commands.UserInputError):
        await ctx.send("Invalid input. Please use `,help` for instructions on how to use this command.")
        # await ctx.command.send_command_help(ctx) TODO
        return

    if isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send('This command cannot be used in direct messages.')
        except discord.Forbidden:
            pass
        return

    if isinstance(error, discord.errors.Forbidden):
        logger.warning(error)
        return

    if isinstance(error, commands.CheckFailure):
        await ctx.send(str(error))
        return

    # ignore all other exception types, but print them to stderr
    # noinspection PyBroadException
    try:
        channel_id = config.get('Bot', 'ChannelErrorLog', fallback=None)
        if channel_id:
            channel = ctx.bot.get_channel(int(channel_id))
            app_info = await ctx.bot.application_info()
            tb = ''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))
            await channel.send(content=f"{app_info.owner.mention} An exception has been logged:\n```\n{tb}\n```")
    except Exception:
        logger.trace("Failed to log exception to the specified error logging channel")
    logger.exception("An unknown exception occurred while executing a command", exception=error)
