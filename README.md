# Dice-Bot

How to Install this flimsy dice bot

1) Download the repository
2) Install Python version 3.8 available [here](https://www.python.org/downloads/release/python-385/)
3) Install virtualenv using `pip install virtualenv`
4) Create a Discord Bot on the Discord Developer site [here](https://discordapp.com/developers/applications) and it to your server (instructions to do so can be found [here](https://discordpy.readthedocs.io/en/latest/discord.html))
6) Get the bot token and place in a file name `.env` in the same directory as the `bot.py` file

Now if you are on windows, you can now simply run `runbot.bat` and be done

If you aren't on windows then you may have to do a bit more work
1) Open a terminal
2) `cd` to where the bot.py file is
3) Run the following commands
```
env/scripts/activate
pip install -r requirements.txt
python bot.py
```
