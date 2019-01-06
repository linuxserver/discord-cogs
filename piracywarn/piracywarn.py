"""
The MIT License (MIT)

Copyright (c) 2018 LinuxServer.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging

log_file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
log_file_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))

LOGGER = logging.getLogger('discord')
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(log_file_handler)

import discord 
from discord.ext import commands

KEYWORDS = [
    "seedbox", "seed-box", "piratebay"
]

WARNING_MESSAGE = (
    "A friendly reminder that we do not condone any related discussion regarding pirated material on this server. "
    "Your last message in {} was flagged as potentially in contravention of Rule 3 (See #rules for more information)."
)

class PiracyWarn:
    """
    Listens on all message events and checks them for specific keywords that may suggest
    conversation relating to unwanted material in the server; specifically around piracy
    """

    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot

    async def message(self, message: discord.Message):
        """
        Checks the message contents to see if any of the words used match any specific keywords
        """

        server = message.server

        if server is not None:

            message_words = message.content.split(' ')
            message_member = server.get_member(message.author.id)

            for keyword in KEYWORDS:                
                if keyword in message_words:
                    
                    await self.bot.send_message(message_member, WARNING_MESSAGE.format(message.channel.name))
                    break

def setup(bot):

    cog = PiracyWarn(bot)

    bot.add_listener(cog.message, "on_message")
    bot.add_cog(cog)