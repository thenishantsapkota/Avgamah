import tanjun

from avgamah.utils.permissions import Permissions

permissions = Permissions()

emoji_group = tanjun.slash_command_group("emoji", "Group that handles emoji operations")

color_dict: dict[str, int] = {
    "Crimson": 0x990000,
    "Green": 0x00FF00,
    "Yellow": 0xFFFF00,
    "Cyan": 0x00FFFF,
    "Magenta": 0xFF00FF,
    "Red": 0xFF0000,
    "Orange": 0xFFA500,
    "Blurple": 0x7289DA,
    "Silver": 0xAAB9CD,
    "Pink": 0xFFC0CB,
}
