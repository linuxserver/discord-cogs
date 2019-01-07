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

SETTINGS = {
    'greeting': "Welcome to the LinuxServer.io Discord server {}! We kindly ask that you first read our {}. Once you're happy, say `^readrules` in this channel to get access to all of our public channels.",
    'elevate_confirm': "Thanks, you now have access to all public channels!",
    'already_verified': "You already have access to our public channels.",
    'base_role': "verified",
    'default_channel': "new-members",
    'rules_channel': "rules"
}

class Welcome:
    """
    Provides new users with a welcome message, which can be either to give them
    a basic guide to the server, or can prompt them to call back to the bot via
    a specific command
    """

    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def readrules(self, ctx: commands.bot.Context):
        """
        Elevates a user's access to all public channels
        """

        server = ctx.message.server

        # User likely invoked command from a DM
        if server is None:
            LOGGER.info("Command invoked via DM. Ignoring.")

        else:
            
            member_to_elevate = server.get_member(ctx.message.author.id)

            LOGGER.info("User {} invoked readrules command.".format(member_to_elevate))

            member_already_user = False
            for role in member_to_elevate.roles:
                
                if role.name == SETTINGS['base_role']:

                    LOGGER.info("Member {} already has a {} role".format(member_to_elevate, SETTINGS['base_role']))
                    member_already_user = True
                    await self.bot.send_message(member_to_elevate, SETTINGS['already_verified'])

            if not member_already_user:

                LOGGER.info("Adding role {} to member {}".format(SETTINGS['base_role'], member_to_elevate))
                base_role = discord.utils.get(server.roles, name=SETTINGS['base_role'])

                await self.bot.add_roles(member_to_elevate, base_role)
                await self.bot.send_message(member_to_elevate, SETTINGS['elevate_confirm'])

    async def member_join(self, member: discord.Member):
        """
        Sends a welcome message to a newly joined member
        """

        LOGGER.info("New member has joined: {}".format(member))

        channels = member.server.channels

        channel_new_members = discord.utils.get(channels, name=SETTINGS['default_channel'])
        channel_rules = discord.utils.get(channels, name=SETTINGS['rules_channel'])

        await self.bot.send_message(channel_new_members, SETTINGS['greeting'].format(member.mention, channel_rules.mention))

def setup(bot):

    cog = Welcome(bot)

    bot.add_listener(cog.member_join, "on_member_join")
    bot.add_cog(cog)
