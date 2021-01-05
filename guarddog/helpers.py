import ipaddress
import logging
import re
import socket
from urllib.parse import urlparse

import typing

import guarddog.assets
from guarddog.bot import bot

import discord

_log = logging.getLogger(__name__)

# https://daringfireball.net/2010/07/improved_regex_for_matching_urls
URL_REGEX = re.compile(r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")


def validate_url(url: str, deny_localhost=True, timeout=3) -> bool:
    """
    Validates a web URL and (optionally) rejects localhost URL's
    @param url: URL to validate
    @param deny_localhost: Deny validation on localhost/private IP's if True
    @param timeout: Timeout for hostname resolve requests
    """
    socket.setdefaulttimeout(timeout)

    # Make sure we pass a "basic" URL validation check
    if not URL_REGEX.match(url):
        _log.debug("URL failed to match: " + url)
        return False

    parsed_url = urlparse(url)

    # If a scheme was defined, make sure it is either http or https
    if parsed_url.scheme:
        if parsed_url.scheme not in ['http', 'https']:
            _log.debug("URL scheme is invalid: " + url)
            return False
    else:
        parsed_url = urlparse("http://" + url)  # otherwise, urlparse won't recognize the hostname

    # Make sure the host isn't localhost
    if parsed_url.hostname == 'localhost' and deny_localhost:
        _log.debug("URL is localhost: " + url)
        return False

    # Attempt to resolve the host and make sure it's not a private address space
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(parsed_url.hostname))
    except socket.error:
        _log.debug("Failed to resolve URL: " + url)
        return False

    if ip.is_private and deny_localhost:
        _log.debug("URL resolves to a private address space: " + url)
        return False

    # Still here? Everything looks good then!
    _log.debug("URL successfully validated: " + url)
    return True


def get_gender(member: discord.Member, noun=False, their=False):
    """
    Return the specified members gender, if available
    """
    guild = member.guild  # type: discord.Guild
    bedwetter   = guild.get_role(606123174144245791)
    daddy       = guild.get_role(665330639918071818)
    male        = guild.get_role(524423858401312768)
    female      = guild.get_role(524424159908855810)
    them        = guild.get_role(524424349487464448)

    if daddy in member.roles:
        return "daddy's" if their else 'daddy'

    if bedwetter in member.roles:
        return "the bedwetter's" if their else 'the bedwetter'

    if male in member.roles:
        return 'he' if noun else 'his' if their else 'him'

    if female in member.roles:
        return 'she' if noun else 'her'

    if them in member.roles:
        return 'they' if noun else 'their' if their else 'them'

    return 'they' if noun else 'their' if their else 'them'


def reaction_check(message: discord.Message, authorized_users: typing.List[int], valid_emojis: typing.List[str]):
    def _inner_check(_reaction: discord.Reaction, _user: discord.User):
        if message.id != _reaction.message.id:
            _log.debug(f"[Reaction check] Wrong message (Expecting {message.id}, got {_reaction.message.id})")
            return False

        if _user.id not in authorized_users:
            _log.debug(f"[Reaction check] Unauthorized user: {_user.id}")
            return False

        if str(_reaction.emoji) not in valid_emojis:
            _log.debug(f"[Reaction check] Invalid emoji: {_reaction.emoji}")
            return False

        _log.debug("[Reaction check] Check passed!")
        return True

    return _inner_check


def keycap_emoji(number: int) -> str:
    """
    Helper function for getting a 0-10 keycap emoji, since these are inherently weird
    """
    # Only keycaps between 0 and 10 are supported
    if not 0 <= number <= 10:
        raise IndexError

    # 10 is unique
    if number == 10:
        return "\N{keycap ten}"

    return str(number) + "\N{variation selector-16}\N{combining enclosing keycap}"


def keycap_to_int(emoji: discord.Emoji) -> int:
    """
    Converts a keycap emoji back to an integer
    Used to help when prompting users to select an index with keycap reactions
    """
    if str(emoji) == '\N{keycap ten}':
        return 10
    else:
        return int(str(emoji)[0])


def say(*, message: str, mood: typing.Optional[str] = guarddog.assets.MOOD_NORMAL, face: str = guarddog.assets.FACE_TALKING, footer: bool = False) -> discord.Embed:
    """
    Gets a speech bubble formatted embed
    """
    embed = discord.Embed()
    mood = bot.get_emoji(mood) if mood else None  # type: discord.Emoji

    if face:
        embed.set_thumbnail(url=face)

    if footer:
        if mood:
            embed.set_footer(text=message, icon_url=mood.url)
        else:
            embed.set_footer(text=message)
    else:
        if mood:
            embed.description = f"{mood} {message}"
        else:
            embed.description = message

    return embed

