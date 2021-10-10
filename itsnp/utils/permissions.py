from operator import attrgetter
from typing import Any, Iterable, Optional, TypeVar, Union

import hikari
import tanjun

T = TypeVar("T")

from models import ModerationRoles


class NotEnoughPermissions(tanjun.CommandError):
    pass


class SetModerationRoles(tanjun.CommandError):
    pass


class NotHigherRole(tanjun.CommandError):
    pass


def get(iterable: Iterable[T], **attrs: Any) -> Optional[T]:
    """A helper that returns the first element in the iterable that meets
    all the traits passed in ``attrs``.
    Args:
        iterable (Iterable): An iterable to search through.
        **attrs (Any): Keyword arguments that denote attributes to search with.
    """
    attrget = attrgetter

    # Special case the single element call
    if len(attrs) == 1:
        k, v = attrs.popitem()
        pred = attrget(k.replace("__", "."))
        for elem in iterable:
            if pred(elem) == v:
                return elem
        return None

    converted = [
        (attrget(attr.replace("__", ".")), value) for attr, value in attrs.items()
    ]

    for elem in iterable:
        if all(pred(elem) == value for pred, value in converted):
            return elem
    return None


class Permissions:
    """Custom class for checking guild settings to handle moderation commands."""

    async def has_permissions(
        self, member: hikari.Member, permission: list[hikari.Permissions]
    ) -> bool:
        roles = member.get_roles()
        perms = hikari.Permissions.NONE

        for r in roles:
            perms |= r.permissions

        permissions = str(perms).split("|")
        if set(permission) & set(permissions):
            return True
        return False

    async def rolecheck(self, member: hikari.Member, role: hikari.Role) -> bool:
        if role.id in member.role_ids:
            return True
        return False

    async def fetch_role_data(self, guild: hikari.Guild) -> dict:
        model = await ModerationRoles.get_or_none(guild_id=guild.id)
        if model is None:
            raise SetModerationRoles(
                """Please setup moderation roles before using any moderation commands.
            Use `/role admin <roleid>`, `/role mod <roleid>`, `/role staff <roleid>` to set moderation roles.
            """
            )
        admin_role = guild.get_role(model.admin_role)
        mod_role = guild.get_role(model.mod_role)
        staff_role = guild.get_role(model.staff_role)

        roles = {"adminrole": admin_role, "modrole": mod_role, "staffrole": staff_role}
        return roles

    async def staff_role_check(
        self, ctx: tanjun.abc.Context, guild: hikari.Guild
    ) -> None:
        staff_role = (await self.fetch_role_data(guild)).get("staffrole")
        if not (
            await self.has_permissions(ctx.member, ["MANAGE_MESSAGES", "ADMINISTRATOR"])
            or await self.rolecheck(ctx.member, staff_role)
        ):
            raise tanjun.CommandError(
                f"You don't have the required permissions or,\nYou don't have {staff_role.mention} role to run this command.<:jhyama:889855700229058640>"
            )

    async def mod_role_check(
        self, ctx: tanjun.abc.Context, guild: hikari.Guild
    ) -> None:
        mod_role = (await self.fetch_role_data(guild)).get("modrole")
        if not (
            await self.has_permissions(ctx.member, ["MANAGE_ROLES", "ADMINISTRATOR"])
            or await self.rolecheck(ctx.member, mod_role)
        ):
            raise tanjun.CommandError(
                f"You don't have the required permissions or,\nYou don't have {mod_role.mention} role to run this command.<:jhyama:889855700229058640>"
            )

    async def admin_role_check(
        self, ctx: tanjun.abc.Context, guild: hikari.Guild
    ) -> None:
        admin_role = (await self.fetch_role_data(guild)).get("adminrole")
        if not (
            await self.has_permissions(ctx.member, ["ADMINISTRATOR"])
            or await self.rolecheck(ctx.member, admin_role)
        ):
            raise tanjun.CommandError(
                f"You don't have the required permissions or,\nYou don't have {admin_role.mention} role to run this command.<:jhyama:889855700229058640>"
            )

    async def log_channel_check(
        self, ctx: tanjun.abc.Context, guild: hikari.Guild
    ) -> hikari.GuildTextChannel:
        log_channel = get(await ctx.rest.fetch_guild_channels(guild), name="mod-logs")
        if log_channel is None:
            log_channel = await guild.create_text_channel(name="mod-logs")
            await log_channel.edit_overwrite(
                target=guild.get_role(guild.id),
                deny=hikari.Permissions.VIEW_CHANNEL | hikari.Permissions.SEND_MESSAGES,
            )
        return log_channel

    async def member_logging_check(
        self, guild: hikari.Guild
    ) -> hikari.GuildTextChannel:
        log_channel = get(guild.get_channels(), name="member-logs")
        if log_channel is None:
            log_channel = await guild.create_text_channel(name="member-logs")
            await log_channel.edit_overwrite(
                target=guild.get_role(guild.id),
                deny=hikari.Permissions.VIEW_CHANNEL | hikari.Permissions.SEND_MESSAGES,
            )
        return log_channel

    async def server_logging_check(
        self, guild: hikari.Guild
    ) -> hikari.GuildTextChannel:
        log_channel = get(guild.get_channels(), name="server-logs")
        if log_channel is None:
            log_channel = await guild.create_text_channel(name="server-logs")
            await log_channel.edit_overwrite(
                target=guild.get_role(guild.id),
                deny=hikari.Permissions.VIEW_CHANNEL | hikari.Permissions.SEND_MESSAGES,
            )
        return log_channel

    async def voice_logging_check(self, guild: hikari.Guild) -> hikari.GuildTextChannel:
        log_channel = get(guild.get_channels(), name="voice-logs")
        if log_channel is None:
            log_channel = await guild.create_text_channel(name="voice-logs")
            await log_channel.edit_overwrite(
                target=guild.get_role(guild.id),
                deny=hikari.Permissions.VIEW_CHANNEL | hikari.Permissions.SEND_MESSAGES,
            )
        return log_channel

    async def message_logging_check(
        self, guild: hikari.Guild
    ) -> hikari.GuildTextChannel:
        log_channel = get(guild.get_channels(), name="message-logs")
        if log_channel is None:
            log_channel = await guild.create_text_channel(name="message-logs")
            await log_channel.edit_overwrite(
                target=guild.get_role(guild.id),
                deny=hikari.Permissions.VIEW_CHANNEL | hikari.Permissions.SEND_MESSAGES,
            )
        return log_channel

    async def muted_role_check(
        self, ctx: tanjun.abc.Context, guild: hikari.Guild
    ) -> hikari.Role:
        muted_role = get(await ctx.rest.fetch_roles(guild), name="Muted")
        if muted_role is None:
            muted_role = await ctx.rest.create_role(guild, name="Muted")
            for channel in await ctx.rest.fetch_guild_channels(guild):
                await channel.edit_overwrite(
                    muted_role,
                    deny=hikari.Permissions.SEND_MESSAGES | hikari.Permissions.SPEAK,
                )
        return muted_role

    async def check_higher_role(
        self, author: hikari.Member, member: hikari.Member
    ) -> None:
        author_top_role = author.get_top_role()
        member_top_role = member.get_top_role()

        if not author_top_role.position > member_top_role.position:
            raise tanjun.CommandError(
                "**You cannot run moderation actions on the users on same rank as you or higher than you.<:jhyama:889855700229058640>**"
            )

    async def check_booster_role(
        self, member: hikari.Member
    ) -> Union[hikari.Role, None]:
        for role in member.get_roles():
            if role.is_premium_subscriber_role:
                booster_role = role
                return booster_role
