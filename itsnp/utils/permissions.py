from datetime import datetime

import hikari
import lightbulb
import tanjun

from itsnp.core.models import ModerationRoles


class NotEnoughPermissions(tanjun.CommandError):
    pass


class SetModerationRoles(tanjun.CommandError):
    pass


class NotHigherRole(tanjun.CommandError):
    pass


class Permissions:
    """Custom class for checking guild settings to handle moderation commands."""

    async def has_permissions(
        self, member: hikari.Member, permission: hikari.Permissions
    ) -> bool:
        roles = member.get_roles()
        perms = hikari.Permissions.NONE

        for r in roles:
            perms |= r.permissions

        permissions = str(perms).split("|")
        if permission in permissions:
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
            await self.has_permissions(ctx.member, "MANAGE_MESSAGES")
            or await self.rolecheck(ctx.member, staff_role)
        ):
            raise tanjun.CommandError(
                f"You don't have the required permissions or,\nYou don't have {staff_role.mention} role to run this command.<:jhyama:883390821397831701>"
            )

    async def mod_role_check(
        self, ctx: tanjun.abc.Context, guild: hikari.Guild
    ) -> None:
        mod_role = (await self.fetch_role_data(guild)).get("modrole")
        if not (
            await self.has_permissions(ctx.member, "MANAGE_ROLES")
            or await self.rolecheck(ctx.member, mod_role)
        ):
            raise tanjun.CommandError(
                f"You don't have the required permissions or,\nYou don't have {mod_role.mention} role to run this command.<:jhyama:883390821397831701>"
            )

    async def admin_role_check(
        self, ctx: tanjun.abc.Context, guild: hikari.Guild
    ) -> None:
        admin_role = (await self.fetch_role_data(guild)).get("adminrole")
        if not (
            await self.has_permissions(ctx.member, "ADMINISTRATOR")
            or await self.rolecheck(ctx.member, admin_role)
        ):
            raise tanjun.CommandError(
                f"You don't have the required permissions or,\nYou don't have {admin_role.mention} role to run this command.<:jhyama:883390821397831701>"
            )

    async def log_channel_check(
        self, ctx: tanjun.abc.Context, guild: hikari.Guild
    ) -> hikari.GuildTextChannel:
        channels = ctx.cache.get_guild_channels_view_for_guild(ctx.guild_id)
        log_channel = next(
            filter(
                lambda channel: channel.name == "mod-logs",
                ctx.cache.get_guild_channels_view,
            ),
            None,
        )
        print(log_channel)
