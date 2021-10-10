# Hikari-Bot

This is a Open-Sourced General Purpose Bot for Discord made using [Hikari](https://github.com/hikari-py/hikari) and [Tanjun](https://github.com/FasterSpeeding/Tanjun).

This bot implements Slash Commands in the guild which are a new-ish feature of Discord.

To invite this bot to your server, [click here](https://discord.com/api/oauth2/authorize?client_id=857596690637783080&permissions=8&scope=bot%20applications.commands)

**What this Bot can do?**

- Fun Commands (coming soon...)
- Miscellaneous Commands like Weather Lookup and more coming soon...
- Moderation Commands like `kick`, `mute`, `ban` with intensive permission checks and much more.
- Music Commands to play music in your server using [lavasnek_rs](https://github.com/vicky5124/lavasnek_rs)
- More commands coming soon...


**How to run this bot locally?**

First of all check `.env.example` for Examples on environment variables.

To run this bot locally, you need to have a PostgreSQL database setup and running.

Clone the repository using
```bash
git clone https://github.com/thenishantsapkota/Hikari-Bot
poetry shell
poetry install
```
To use `poetry shell` you need to have [poetry](https://python-poetry.org/) installed on your path.
That will initialize a virtual environment for the bot to work in.

The `poetry install` command will install all the necessary requirements for the bot to run within the VirtualEnvironment.

Before proceeding, Be sure to check `tortoise_config.py.example` to setup your `tortoise_config.py` accordingly.

After sucessfully installing all the dependencies, do this when your PostgreSQL database is running.

```bash
aerich init -t tortoise_config.tortoise_config
aerich init-db
```

This will initialize all the models and setup the database for your use.

Then finally run this command to start the bot.

```bash
python -OO -m itsnp
```



