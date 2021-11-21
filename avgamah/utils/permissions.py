from __future__ import annotations

import hikari
import tanjun

from models import ModerationRoles

from .utilities import get


class Permissions:
    """Custom class for checking guild settings to handle moderation commands."""

    async def has_permissions(
        self, member: hikari.Member, permission: list[hikari.Permissions]
    ) -> bool:
        """
        Function that checks if user has correct permissions or the correct roles

        Parameters
        ----------
        member : hikari.Member
            Member on whom the check is to be performed
        permission : list[hikari.Permissions]
            Permissions to be checked against the user.

        Returns
        -------
        bool
            Returns True if member has required permissions else returns False
        """
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
            raise tanjun.CommandError(
                """
            Please setup moderation roles before using any moderation commands.
            Use `/role admin <roleid>`, `/role mod <roleid>`, `/role staff <roleid>` to set moderation roles.
            """
            )
        admin_role = guild.get_role(model.admin_role)
        mod_role = guild.get_role(model.mod_role)
        staff_role = guild.get_role(model.staff_role)

        roles = {
            "adminrole": admin_role,
            "modrole": mod_role,
            "staffrole": staff_role,
        }
        return roles

    async def staff_role_check(
        self, ctx: tanjun.abc.Context, guild: hikari.Guild
    ) -> None:
        """
        Function that checks if user has "Staff Role" or the "Manage Messages" permission.

        Parameters
        ----------
        ctx : tanjun.abc.Context
            Context of the command invkokation
        guild : hikari.Guild
            Guild where the check is to be done.

        Raises
        ------
        tanjun.CommandError
            Raised when user doesn't have the required permissions.
        """
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
        """
        Function that checks if user has "Mod Role" or the "Manage Roles" permission.

        Parameters
        ----------
        ctx : tanjun.abc.Context
            Context of the command invkokation
        guild : hikari.Guild
            Guild where the check is to be done.

        Raises
        ------
        tanjun.CommandError
            Raised when user doesn't have the required permissions.
        """
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
        """
        Function that checks if user has "Administrator Role" or the "Administrator" permission.

        Parameters
        ----------
        ctx : tanjun.abc.Context
            Context of the command invkokation
        guild : hikari.Guild
            Guild where the check is to be done.

        Raises
        ------
        tanjun.CommandError
            Raised when user doesn't have the required permissions.
        """
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
        """
        Function that checks for "mod-logs" channel in a guild, if not it creates one

        Parameters
        ----------
        ctx : tanjun.abc.Context
            Context of the command invokation
        guild : hikari.Guild
            Guild in which log channel is to be checked

        Returns
        -------
        hikari.GuildTextChannel
            Returns TextChannel object of "mod-logs" channel.
        """
        log_channel = get(await ctx.rest.fetch_guild_channels(guild), name="mod-logs")
        if log_channel is None:
            log_channel = await guild.create_text_channel(name="mod-logs")
            await log_channel.edit_overwrite(
                target=guild.get_role(guild.id),
                deny=hikari.Permissions.VIEW_CHANNEL | hikari.Permissions.SEND_MESSAGES,
            )
        return log_channel

    async def muted_role_check(
        self, ctx: tanjun.abc.Context, guild: hikari.Guild
    ) -> hikari.Role:
        """
        Function that checks for muted role in the guild

        Parameters
        ----------
        ctx : tanjun.abc.Context
            Context of the command invokation
        guild : hikari.Guild
            Guild in which muted role is to be checked.

        Returns
        -------
        hikari.Role
            Returns the "Muted" role by creating if it doesn't exist or returns the role by fetching the role.
        """
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
        """
        Function that checks if the command author has higher role than the member

        Parameters
        ----------
        author : hikari.Member
            Author of the Command Invokation
        member : hikari.Member
            Member against whom author's permissions are to be checked

        Raises
        ------
        tanjun.CommandError
            Error raised when Author role is not higher than Member's top role
        """
        author_top_role = author.get_top_role()
        member_top_role = member.get_top_role()

        if not author_top_role.position > member_top_role.position:
            raise tanjun.CommandError(
                "**You cannot run moderation actions on the users on same rank as you or higher than you.<:jhyama:889855700229058640>**"
            )

    async def check_booster_role(self, member: hikari.Member) -> hikari.Role | None:
        """
        Function that checks for booster role in the guild

        Parameters
        ----------
        member : hikari.Member
            Member on whom the role is to be checked

        Returns
        -------
        hikari.Role | None
            Gets the booster role if exists on the member else returns None
        """
        for role in member.get_roles():
            if role.is_premium_subscriber_role:
                booster_role = role
                return booster_role
