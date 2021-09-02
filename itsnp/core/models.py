"""Models file to generate models for tortoise-orm"""
from tortoise import fields
from tortoise.models import Model


class GuildModel(Model):
    """Defining a guild model to store prefix of the guild"""

    guild_id = fields.BigIntField(pk=True)
    prefix = fields.TextField(default=">")

    class Meta:
        """Meta class to set table name and description"""

        table = "guild"
        table_description = "Stores information about the guild"
