import hikari
import tanjun

from avgamah.utils.permissions import Permissions

permissions = Permissions()

role_group = tanjun.SlashCommandGroup(
    "role", "Set moderation roles for the server"
).add_check(
    tanjun.AuthorPermissionCheck(
        hikari.Permissions.ADMINISTRATOR,
        error_message="You need **Administrator** permission(s) to run this command.",
    )
)
