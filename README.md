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


Clone the repository using
```bash
git clone https://github.com/thenishantsapkota/Hikari-Bot
poetry shell
poetry install
```

You need to have Docker Installed on your system.

Afer cloning 
```bash
cd Avgamah
```

Then run 
```bash
docker-compose up --build # Linux users have to use sudo
```

You're up and running!


