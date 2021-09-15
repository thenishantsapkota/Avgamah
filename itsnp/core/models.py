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


class TagModel(Model):
    """Defining a tag model to store tags"""

    name_tag = fields.TextField(null=True)
    tag_value = fields.TextField(null=True)
    guild_id = fields.BigIntField(null=True)

    class Meta:
        """Meta class to set table name and description"""

        table = "tags"
        table_description = "Stores all the tags"


class ModerationRoles(Model):
    """Defining a moderation roles model to store moderation roles for the server"""

    id = fields.IntField(pk=True)
    admin_role = fields.BigIntField(null=True)
    mod_role = fields.BigIntField(null=True)
    staff_role = fields.BigIntField(null=True)
    guild_id = fields.BigIntField()

    class Meta:
        """Meta class to set table name and description"""

        table = "staffroles"
        table_description = "Stores StaffRoles of the server"
