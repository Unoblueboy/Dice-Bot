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
            file.write(json.dumps({}))

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
    name_status = addname_cmd(id, name)
    if name_status == 0:
        await ctx.send("You aren't registered, please register using /register")
    elif name_status == 1:
        await ctx.send("{} is now {}".format(ctx.author.name, name))
    else:
        await ctx.send("You already have a name, use `/name edit` to change it.")


def addname_cmd(id, name):
    data = get_data()
    if id not in data:
        return 0 # not registered
    elif data[id]["name"] is None:
        data[id]["name"] = name
        update_data(data)
        return 1 # succesfully registered
    else:
        return 2 # already in database


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
    name_status = editname_cmd(id, name)
    if name_status == 0:
        await ctx.send("You aren't registered, please register using /register")
    elif name_status == 1:
        await ctx.send("{} is now {}".format(ctx.author.name, name))
    else:
        await ctx.send("You don't have a name, use `/name add` to add one.")


def editname_cmd(id, name):
    data = get_data()
    if id not in data:
        return 0
    elif data[id]["name"] is not None:
        data[id]["name"] = name
        update_data(data)
        return 1
    else:
        return 2


@slash.subcommand(base = "name", name="delete",
                guild_ids = guild_ids,
                description = "Delete Your Character name from the Database",
                )
async def deletename(ctx):
    id = str(ctx.author.id)
    name_status = deletename_cmd(id)
    if name_status == 0:
        await ctx.send("You aren't registered, please register using /register")
    elif name_status == 1:
        await ctx.send("{} now has no name".format(ctx.author.name))
    else:
        await ctx.send("You don't have a name, so there is nothing to delete.")


def deletename_cmd(id):
    data = get_data()
    if id not in data:
        return 0
    elif data[id]["name"] is not None:
        data[id]["name"] = None
        update_data(data)
        return 1
    else:
        return 2


@slash.subcommand(base = "name", name="get",
                guild_ids = guild_ids,
                description = "Get Your Character name from the Database",
                )
async def getname(ctx):
    id = str(ctx.author.id)
    name_status, name = getname_cmd(id)
    if name_status == 0:
        await ctx.send("You aren't registered, please register using /register")
    elif name_status == 1:
        await ctx.send("{} is {}".format(ctx.author.name, name))
    else:
        await ctx.send("You don't have a name, so there is no name to get.")


def getname_cmd(id):
    data = get_data()
    if id not in data:
        return (0, "")
    if data[id]["name"] is not None:
        return (1, data[id]["name"])
    else:
        return (2, "")

# -----------------------------------------------------------------------------

def roll_message(id, dice_string, name = None):
    data = get_data()
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
            message = "<@{}>: `{}` = {} = {}".format(id,
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
            message = ( "<@{}>: You're rolling too many dice,"
                        " the result can't be displayed").format(id)
        return (1, message)
    except Exception as e:
        print(e)
        return (2,"<@{}>: There has been an error".format(id))


@slash.subcommand(base="roll", name="dice",
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
    id = str(ctx.author.id)

    _, message = roll_message(id, dice_string, name)
    await ctx.send(message)


@bot.command()
async def r(ctx):
    await ctx.trigger_typing()
    input_str = ctx.message.content[3:]
    parts = input_str.split("#")
    if len(parts) > 1:
        name = parts[1].strip()
    else:
        name = None
    dice_string = parts[0].strip()
    id = str(ctx.author.id)

    _, message = roll_message(id, dice_string, name)
    await ctx.send(message)


@slash.subcommand(base = "roll", name="add",
                guild_ids = guild_ids,
                description = "Save a dice roll to the Database",
                options = [
                    create_option(
                            name="Dice_String",
                            description="String representing dice roll + modifiers",
                            option_type=3,
                            required=True
                         ),
                    create_option(
                            name="Roll_Name",
                            description="The Name of Your saved roll",
                            option_type=3,
                            required=True
                         )
                    ]
                )
async def addroll(ctx, dice_string: str, roll_name: str):
    id = str(ctx.author.id)
    roll_status = addroll_cmd(id, dice_string, roll_name)
    if roll_status == 0:
        await ctx.send("You aren't registered, please register using /register")
    elif roll_status == 1:
        await ctx.send("The Roll has been saved to the database")
    else:
        await ctx.send("You already have a roll with this name, use `/roll edit` to change it.")


def addroll_cmd(id, dice_string, roll_name):
    data = get_data()
    if id not in data:
        return 0 # not registered
    elif roll_name not in data[id]["rolls"]:
        data[id]["rolls"][roll_name] = dice_string
        update_data(data)
        return 1 # succesfully registered
    else:
        return 2 # already in database


@slash.subcommand(base = "roll", name="saved",
                guild_ids = guild_ids,
                description = "Roll a dice roll saved in the database",
                options = [
                    create_option(
                            name="Roll_Name",
                            description="The Name of Your saved roll",
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
async def rollsaved(ctx, roll_name, name = None):
    id = str(ctx.author.id)
    roll_status, message = rollsaved_cmd(id, roll_name, name)
    if roll_status == 0:
        await ctx.send("You aren't registered, please register using /register")
    elif roll_status == 1:
        await ctx.send(message)
    else:
        await ctx.send("You don't have a roll with this name, use `/roll add` to change it.")


def rollsaved_cmd(id, roll_name, name):
    data = get_data()
    if id not in data:
        return (0,"") # not registered
    elif roll_name in data[id]["rolls"]:
        dice_string = data[id]["rolls"][roll_name]
        _, message = roll_message(id, dice_string, name)
        return (1, message) # succesfully registered
    else:
        return (2, "") # roll name not in database


@slash.subcommand(base = "roll", name="delete",
                guild_ids = guild_ids,
                description = "Delete a dice roll saved in the database",
                options = [
                    create_option(
                            name="Roll_Name",
                            description="The Name of Your saved roll",
                            option_type=3,
                            required=True
                         )
                    ]
                )
async def rolldelete(ctx, roll_name):
    id = str(ctx.author.id)
    roll_status = rolldelete_cmd(id, roll_name)
    if roll_status == 0:
        await ctx.send("You aren't registered, please register using /register")
    elif roll_status == 1:
        await ctx.send("{} has been deleted from your saved rolls".format(roll_name))
    else:
        await ctx.send("You don't have a roll with this name, so there was nothing to delete")


def rolldelete_cmd(id, roll_name):
    data = get_data()
    if id not in data:
        return 0 # not registered
    elif roll_name in data[id]["rolls"]:
        del data[id]["rolls"][roll_name]
        update_data(data)
        return 1 # succesfully registered
    else:
        return 2 # roll name not in database


@slash.subcommand(base = "roll", name="edit",
                guild_ids = guild_ids,
                description = "Edit a dice roll saved in the Database",
                options = [
                    create_option(
                            name="Dice_String",
                            description="String representing dice roll + modifiers",
                            option_type=3,
                            required=True
                         ),
                    create_option(
                            name="Roll_Name",
                            description="The Name of Your saved roll",
                            option_type=3,
                            required=True
                         )
                    ]
                )
async def editroll(ctx, dice_string: str, roll_name: str):
    id = str(ctx.author.id)
    roll_status = editroll_cmd(id, dice_string, roll_name)
    if roll_status == 0:
        await ctx.send("You aren't registered, please register using /register")
    elif roll_status == 1:
        await ctx.send("The Roll has been edited in the database")
    else:
        await ctx.send("You don't have a roll with this name, use `/roll add` to add one.")


def editroll_cmd(id, dice_string, roll_name):
    data = get_data()
    if id not in data:
        return 0 # not registered
    elif roll_name in data[id]["rolls"]:
        data[id]["rolls"][roll_name] = dice_string
        update_data(data)
        return 1 # succesfully registered
    else:
        return 2 # already in database

@slash.subcommand(base = "roll", name="view",
                guild_ids = guild_ids,
                description = "View all dice rolls saved in the database",
                )
async def viewroll(ctx):
    id = str(ctx.author.id)
    roll_status, message = viewroll_cmd(id)
    if roll_status == 0:
        await ctx.send("You aren't registered, please register using /register")
    elif roll_status == 1:
        await ctx.author.send(message)
        await ctx.send("All Possible rolls has been sent to you via DMs")
    else:
        await ctx.send("You don't have any saved rolls to be shown")

def viewroll_cmd(id):
    data = get_data()
    if (id not in data):
        return (0, "") # not registered
    elif len(data[id]["rolls"]) > 0:
        message_list = ["{}: {}".format(k, v) for k, v in data[id]["rolls"].items()]
        message = "\n".join(message_list)
        message = "```" + message + "```"
        return (1, message) # return all rolls
    else:
        return (2, "") # no rolls to show


@bot.event
async def on_ready():
    client_id = bot.user.id
    print(oauth_url(str(client_id),
    permissions=Permissions(2147485696),
    scopes = ('bot', 'applications.commands')))


if __name__ == '__main__':

    initialize()

    from dotenv import load_dotenv
    load_dotenv()
    bot.run(os.environ.get("TOKEN"))
