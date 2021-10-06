import os

from itsnp.core import Bot

bot = Bot()

if os.name != "nt":
    import uvloop

    uvloop.install()

if __name__ == "__main__":
    bot.run()
