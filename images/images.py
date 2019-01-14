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

import re
import requests
import logging

log_file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
log_file_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))

LOGGER = logging.getLogger('discord')
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(log_file_handler)

import discord 
from discord.ext import commands

from datetime import datetime

GITHUB_API_URL      = "https://api.github.com/repos/linuxserver/docker-{}/releases/latest"
GITHUB_API_FALLBACK = "https://api.github.com/repos/linuxserver/docker-{}/tags"
GITHUB_REPO_URL     = "https://github.com/linuxserver/docker-{}"

MESSAGE_RELEASE = "LinuxServer.io Image: **{}**.\nLatest application version is `{}`.\nBuilt on {}."
MESSAGE_TAG     = "LinuxServer.io Image: **{}**.\nNot yet migrated to the new pipeline.\nLatest tagged build is `{}`."

DATE_FORMAT_GITHUB = "%Y-%m-%dT%H:%M:%SZ"
DATE_FORMAT_PRETTY = "%d %B %Y at %H:%M:%S"

VERSION_PATTERNS = [
    
    # Original Jenkins build number
    r"([0-9]{3})", 
    
    # New packaging version format
    r"(.+)-pkg-[a-f0-9]{8}-ls[0-9]+"
]

class Images:
    """
    Provides a Discord command so users can check for the latest version released
    for one of LinuxServer's Docker images.

    Usage:
        [p]image <app_name>
    """

    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def image(self, ctx: commands.bot.Context, image_name: str):
        """
        Responds to a user's request for basic information of a Docker image
        """

        server = ctx.message.server
        channel = ctx.message.channel
        
        # User likely invoked command from a DM
        if server is None:
            LOGGER.info("Command invoked via DM. Ignoring.")

        else:
 
            image_to_check = self.clean_image_name(image_name)

            try:

                latest_release = self.get_image_information(image_to_check)
                image_version = self.get_image_version(latest_release)

                build_date = latest_release.get('published_at')
                migrated = build_date is not None
            
                await self.send_embed(channel, image_to_check, image_version, build_date, migrated)

            except Exception as e:
                
                LOGGER.error("Unable to retrieve version information. {}".format(str(e)))
                await self.bot.send_message(channel, "Unable to retrieve version information for **{}**".format(image_to_check))

    async def send_embed(self, channel: discord.Channel, image_name: str, image_version: str, build_date: str, migrated: bool):
        """
        Sends a rich embed to the Discord channel, with link to the given
        LinuxServer Docker image.
        """

        embed = discord.Embed()
        embed.colour = discord.Colour.orange()
        embed.type = "rich"
        embed.set_author(name="LinuxServer.io")
        
        embed.title = "Image information for {}".format(image_name)
        embed.url = GITHUB_REPO_URL.format(image_name)

        if not migrated:
            embed.description = "_Note:_ This image has not yet been migrated to the new pipeline."

        if build_date is not None:
            build_date = datetime.strptime(build_date, DATE_FORMAT_GITHUB).strftime(DATE_FORMAT_PRETTY)

        embed.add_field(name="App Version", value=image_version, inline=False)
        embed.add_field(name="Build Date", value=build_date, inline=False)

        await self.bot.send_message(channel, embed=embed)

    def get_image_information(self, image_name: str):
        """
        Calls the GitHub API for the given image and returns the primary
        JSON payload (only the latest node). If the initial call fails,
        a fallback URL is used to attmpt to get the latest tag instead.
        """

        try:
            
            LOGGER.info("Getting image data for {}".format(image_name))
            response = requests.get(GITHUB_API_URL.format(image_name))
            response.raise_for_status()

            return response.json()

        except:
                        
            LOGGER.info("Original 'release' call failed. Falling back to tags.")
            response = requests.get(GITHUB_API_FALLBACK.format(image_name))
            response.raise_for_status()

            return response.json()[0]

    def clean_image_name(self, image_name: str):
        """
        Strips out the 'linuxserver/' portion of the image name
        if it was provided.
        """

        if "linuxserver/" in image_name:
            return image_name.split('/')[1]

        return image_name
            
    def get_image_version(self, api_json: dict):
        """
        Scans the JSON payload for the name of the tag and attempts
        to match it against known patterns for LSIO image tags. If the
        version is found, it gets returned.
        """

        for pattern in VERSION_PATTERNS:

            match = re.match(pattern, api_json['name'])
            if match:
                return match.group(1)

        return "<unknown>"
    
def setup(bot):
    bot.add_cog(Images(bot))