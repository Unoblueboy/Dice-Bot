# Dice-Bot

How to Install this flimsy dice bot

1) Download the repository
2) Install Python version 3.7 available [here](https://www.python.org/downloads/release/python-377/)
3) Install pipenv using `pip install pipenv`
4) Create a Discord Bot on the Discord Developer site [here](https://discordapp.com/developers/applications) and it to your server (instructions to do so can be found [here](https://discordpy.readthedocs.io/en/latest/discord.html) no permissions need to be specified)
6) Get the bot token and place at the bottom of the file bot.py where it says `"Your Token Here"`

Now if you are on windows, you can now simply run runbot.bat and be done

If you aren't on windows then you have to do a bit more work
1) Open a terminal
2) Move to where the bot.py file is save
3) Run the following commands
```
pipenv install
pipenv run python bot.py
```
