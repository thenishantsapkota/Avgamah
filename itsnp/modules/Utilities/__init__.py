import tanjun

from itsnp.utils.permissions import Permissions

permissions = Permissions()

emoji_group = tanjun.slash_command_group("emoji", "Group that handles emoji operations")
