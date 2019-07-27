# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 03:33:55 2019

@author: Natha
"""

from discord.ext import commands
from Dice import Roll
import os
import json

bot = commands.Bot(command_prefix='/')

if os.path.exists("names.json"):
    with open("names.json", "r") as file:
        names_txt = file.read()
        names = json.loads(names_txt)
else:
    with open("names.json", "w") as file:
        names = {}
        file.write(json.dumps(names))


@bot.command()
async def addname(ctx):
    id = str(ctx.author.id)
    name = ctx.message.content[9:]
    if addname_cmd(id, name):
        await ctx.send("{} is now {}".format(ctx.author.name, name))
    else:
        await ctx.send("Bitch you already have a name, edit that one")

    with open("names.json", "w") as file:
        file.write(json.dumps(names))


def addname_cmd(id, name):
    global names
    if id not in names:
        names[id] = name
        return True
    else:
        return False


@bot.command()
async def editname(ctx):
    id = str(ctx.author.id)
    name = ctx.message.content[10:]
    if editname_cmd(id, name):
        await ctx.send("{} is now {}".format(ctx.author.name, name))
    else:
        await ctx.send("Bitch you don't have a name, add one")

    with open("names.json", "w") as file:
        file.write(json.dumps(names))


def editname_cmd(id, name):
    global names
    if id in names:
        names[id] = name
        return True
    else:
        return False


@bot.command()
async def deletename(ctx):
    id = str(ctx.author.id)
    if deletename_cmd(id):
        await ctx.send("{} now has no name".format(ctx.author.name))
    else:
        await ctx.send("Bitch you can't delete a name you don't have")

    with open("names.json", "w") as file:
        file.write(json.dumps(names))


def deletename_cmd(id):
    global names
    if id in names:
        del names[id]
        return True
    else:
        return False


@bot.command()
async def getname(ctx, name=None):
    id = str(ctx.author.id)
    if getname_cmd(id):
        await ctx.send("{} is {}".format(ctx.author.name, getname_cmd(id)[1]))
    else:
        await ctx.send("Bitch you can't get a name you don't have")

    with open("names.json", "w") as file:
        file.write(json.dumps(names))


def getname_cmd(id):
    global names
    if id in names:
        return (True, names[id])
    else:
        return (False, "")


@bot.command()
async def name(ctx):
    text = ctx.message.content
    words = text.split(" ")
    try:
        command_word = words[1].lower()
        name = " ".join(words[2:])
    except KeyError:
        await ctx.send("Bitch actually say the command and name")
        return

    id = str(ctx.author.id)
    if command_word == 'add':
        if addname_cmd(id, name):
            await ctx.send("{} is now {}".format(ctx.author.name, name))
        else:
            await ctx.send("Bitch you already have a name, edit that one")

    elif command_word == 'get':
        if getname_cmd(id):
            await ctx.send("{} is {}".format(
                ctx.author.name, getname_cmd(id)[1]))
        else:
            await ctx.send("Bitch you can't get a name you don't have")

    elif command_word == 'delete':
        if deletename_cmd(id):
            await ctx.send("{} now has no name".format(ctx.author.name))
        else:
            await ctx.send("Bitch you can't delete a name you don't have")

    elif command_word == 'edit':
        if editname_cmd(id, name):
            await ctx.send("{} is now {}".format(ctx.author.name, name))
        else:
            await ctx.send("Bitch you don't have a name, add one")

    else:
        await ctx.send("Bitch use an actual command")

    with open("names.json", "w") as file:
        file.write(json.dumps(names))


@bot.command()
async def r(ctx):
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
        if id not in names and name is None:
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
        else:
            message = "{} ({}): `{}` = {} = {}".format(ctx.author.mention,
                                                       names[id],
                                                       parts[0].strip(),
                                                       roll.out_str,
                                                       roll.final_result)
        if len(message) > 2000:
            await ctx.send(("{}: You rolling way too many dice my dude,",
                            " the result can't be displayed").format(
                            ctx.author.mention))
            return
        await ctx.send(message)
        if roll.final_result < 5:
            await ctx.send("You're most likely fucked")
        elif roll.final_result > 20:
            await ctx.send("DAMN!")
    except Exception:
        await ctx.send("{}: You fucked up".format(ctx.message.author.mention))


@bot.command()
async def info(ctx):
    await ctx.send(str(ctx.guild.members))

bot.run('MzQ4NTUxNTE1NjI1MDk1MTc4.XTUgtA.rrolOudLlsU8K9VwmngtWKGPhZ8')
