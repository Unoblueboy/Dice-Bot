# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 03:33:55 2019

@author: Natha
"""

from discord.ext import commands
from discord.utils import oauth_url
from discord import Permissions, Embed

from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from Dice import Roll

import os, json

script_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(script_dir, "data.json")

bot = commands.Bot(command_prefix='/')
slash = SlashCommand(bot, sync_commands = True)

guild_ids = [199725359078440960, 469720401925111818]

def initialize():
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            data = {}
            file.write(json.dumps(data))

#"193863384154898432": {"name": "Enthalten"}

def update_data(data):
    with open(file_path, "w") as file:
        file.write(json.dumps(data, indent=4, sort_keys=True))

def get_data():
    with open(file_path, "r") as file:
        data_txt = file.read()
        data = json.loads(data_txt)
    return data


@slash.slash(name = "register",
            guild_ids = guild_ids,
            description = "Register user into the database")
async def register(ctx):
    data = get_data()
    id = str(ctx.author.id)
    if id not in data:
        data[id] = {"name": None,
                    "rolls": {}}
        await ctx.send("{} is now registered in the database".format(ctx.author.name))
    else:
        await ctx.send("{} is already registered in the database".format(ctx.author.name))
    update_data(data)

@slash.slash(name = "deregister",
            guild_ids = guild_ids,
            description = "Removes user from the database")
async def deregister(ctx):
    data = get_data()
    id = str(ctx.author.id)
    if id in data:
        del data[id]
        await ctx.send("{} is now removed from the database".format(ctx.author.name))
    else:
        await ctx.send("{} was already not in the database".format(ctx.author.name))
    update_data(data)


@slash.subcommand(base = "name", name="add",
                guild_ids = guild_ids,
                description = "Add Your Character name to the Database",
                options = [
                    create_option(
                            name="Name",
                            description="The Name of Your Character",
                            option_type=3,
                            required=True
                         )
                    ]
                )
async def addname(ctx, name: str):
    id = str(ctx.author.id)
    if addname_cmd(id, name):
        await ctx.send("{} is now {}".format(ctx.author.name, name))
    else:
        await ctx.send("You already have a name, use `/name edit` to change it.")


def addname_cmd(id, name):
    data = get_data()
    if id not in data:
        data[id] = {"name": name}
        update_data(data)
        return True
    elif data[id]["name"] is None:
        data[id]["name"] = name
        update_data(data)
        return True
    else:
        return False


@slash.subcommand(base = "name", name="edit",
                guild_ids = guild_ids,
                description = "Edit Your Character name in the Database",
                options = [
                    create_option(
                            name="Name",
                            description="The Name of Your Character",
                            option_type=3,
                            required=True
                         )
                    ]
                )
async def editname(ctx, name: str):
    id = str(ctx.author.id)
    if editname_cmd(id, name):
        await ctx.send("{} is now {}".format(ctx.author.name, name))
    else:
        await ctx.send("You don't have a name, use `/name add` to add one.")


def editname_cmd(id, name):
    data = get_data()
    if (id in data) and (data[id]["name"] is not None):
        data[id]["name"] = name
        update_data(data)
        return True
    else:
        return False


@slash.subcommand(base = "name", name="delete",
                guild_ids = guild_ids,
                description = "Delete Your Character name from the Database",
                )
async def deletename(ctx):
    id = str(ctx.author.id)
    if deletename_cmd(id):
        await ctx.send("{} now has no name".format(ctx.author.name))
    else:
        await ctx.send("You don't have a name, so there is nothing to delete.")


def deletename_cmd(id):
    data = get_data()
    if (id in data) and (data[id]["name"] is not None):
        data[id]["name"] = None
        update_data(data)
        return True
    else:
        return False


@slash.subcommand(base = "name", name="get",
                guild_ids = guild_ids,
                description = "Get Your Character name from the Database",
                )
async def getname(ctx):
    id = str(ctx.author.id)
    if getname_cmd(id)[0]:
        await ctx.send("{} is {}".format(ctx.author.name, getname_cmd(id)[1]))
    else:
        await ctx.send("You don't have a name, so there is no name to get.")


def getname_cmd(id):
    data = get_data()
    if (id in data) and (data[id]["name"] is not None):
        return (True, data[id]["name"])
    else:
        return (False, "")


@slash.slash(name="roll",
            guild_ids = guild_ids,
            description = "Add Your Character name to the Database",
            options = [
                create_option(
                        name="Dice_String",
                        description="String representing dice roll + modifiers",
                        option_type=3,
                        required=True
                     ),
                create_option(
                        name="Name",
                        description="Name of character performing the roll (defaults to your character name)",
                        option_type=3,
                        required=False
                     )
                ]
            )
async def roll(ctx, dice_string, name=None):
    data = get_data()

    id = str(ctx.author_id)
    try:
        dice_string = dice_string.strip()
        roll = Roll(dice_string)
        if (id not in data) and (name == None or (len(name) == 0)):
            message = "<@{}>: `{}` = {} = {}".format(id,
                                                  dice_string,
                                                  roll.out_str,
                                                  roll.final_result)
        elif (name is not None) and (len(name) > 0):
            message = "<@{}> ({}): `{}` = {} = {}".format(id,
                                                       name,
                                                       dice_string,
                                                       roll.out_str,
                                                       roll.final_result)
        elif (id in data) and ((data[id]["name"] is None) or
                                (len(data[id]["name"]) == 0)):
            message = "{}: `{}` = {} = {}".format(ctx.author.mention,
                                                  dice_string,
                                                  roll.out_str,
                                                  roll.final_result)
        else:
            message = "<@{}> ({}): `{}` = {} = {}".format(id,
                                                       data[id]["name"],
                                                       dice_string,
                                                       roll.out_str,
                                                       roll.final_result)
        if len(message) > 2000:
            await ctx.send(("<@{}>: You're rolling too many dice,"
                            " the result can't be displayed").format(
                            id))
            return
        await ctx.send(message)
    except Exception as e:
        print(e)
        await ctx.send("<@{}>: There has been an error".format(id))

@bot.command()
async def r(ctx):
    data = get_data()
    await ctx.trigger_typing()
    input_str = ctx.message.content[3:]
    try:
        parts = input_str.split("#")
        if len(parts) > 1:
            name = parts[1].strip()
        else:
            name = None
        roll = Roll(parts[0].strip())
        id = str(ctx.author.id)
        if (id not in data) and (name is None or (len(name) == 0)):
            message = "{}: `{}` = {} = {}".format(ctx.author.mention,
                                                  parts[0].strip(),
                                                  roll.out_str,
                                                  roll.final_result)
        elif name is not None:
            message = "{} ({}): `{}` = {} = {}".format(ctx.author.mention,
                                                       name,
                                                       parts[0].strip(),
                                                       roll.out_str,
                                                       roll.final_result)
        elif (id in data) and ((data[id]["name"] is None) or
                                (len(data[id]["name"]) == 0)):
            message = "{}: `{}` = {} = {}".format(ctx.author.mention,
                                                  parts[0].strip(),
                                                  roll.out_str,
                                                  roll.final_result)
        else:
            message = "{} ({}): `{}` = {} = {}".format(ctx.author.mention,
                                                       data[id]["name"],
                                                       parts[0].strip(),
                                                       roll.out_str,
                                                       roll.final_result)
        if len(message) > 2000:
            await ctx.send(("{}: You're rolling too many dice,"
                            " the result can't be displayed").format(
                            ctx.author.mention))
            return
        await ctx.send(message)
    except Exception:
        await ctx.send("{}: There has been an error".format(ctx.message.author.mention))

initialize()

@bot.event
async def on_ready():
    client_id = bot.user.id
    print(oauth_url(str(client_id),
    permissions=Permissions(2147485696),
    scopes = ('bot', 'applications.commands')))


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    bot.run(os.environ.get("TOKEN"))
