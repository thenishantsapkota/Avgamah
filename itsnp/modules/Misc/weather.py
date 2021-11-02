import os
from datetime import datetime

import aiohttp
import hikari
import tanjun

from itsnp.core.client import Client
from itsnp.utils.buttons import DELETE_ROW, create_source_button

weather_component = tanjun.Component()


@weather_component.with_slash_command
@tanjun.with_own_permission_check(
    hikari.Permissions.SEND_MESSAGES
    | hikari.Permissions.VIEW_CHANNEL
    | hikari.Permissions.EMBED_LINKS
)
@tanjun.with_str_slash_option("city", "A city's name")
@tanjun.as_slash_command("weather", "Get a place's weather.")
async def weather_command(ctx: tanjun.abc.Context, *, city: str) -> None:
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = (
        base_url + "appid=" + (os.environ.get("WEATHER_TOKEN")) + "&q=" + city
    )
    image = "https://icons-for-free.com/iconfiles/png/512/fog+foggy+weather+icon-1320196634851598977.png"
    async with aiohttp.ClientSession() as session:
        async with session.get(complete_url) as resp:
            data = await resp.json()
            try:
                main = data["main"]
                wind = data["wind"]
                weather = data["weather"]
                city = data["name"]
                temperature_in_celcius = int(main["temp"] - 273)
                feelslike_in_celcius = int(main["feels_like"] - 273)
                max_tempr = int(main["temp_max"] - 273)
                min_tempr = int(main["temp_min"] - 273)
                wind = data["wind"]
                speed_wind = wind["speed"]
                weather_description = str(weather[0]["description"]).title()
            except KeyError:
                return await ctx.respond("No City was found :(")
        embed = hikari.Embed(
            color=0xF1C40F,
            timestamp=datetime.now().astimezone(),
            title=f"Weather of {city.title()}",
        )

    fields = [
        ("Temperature", f"{temperature_in_celcius} °C", True),
        ("Feels Like", f"{feelslike_in_celcius} °C", True),
        ("Maximum Temperature", f"{max_tempr} °C", True),
        ("Minimum Temperature", f"{min_tempr} °C", True),
        ("Description", weather_description, True),
        ("Wind Velocity", f"{speed_wind} km/h", True),
    ]
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    embed.set_thumbnail(image)

    button = create_source_button(ctx, "https://openweathermap.org/api")
    await ctx.respond(embed=embed, components=[button, DELETE_ROW])


@tanjun.as_loader
def load_components(client: Client):
    client.add_component(weather_component.copy())
