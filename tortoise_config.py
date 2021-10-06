"""Configuration file for  tortoise-orm"""
tortoise_config = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": "bot_db",
                "host": "localhost",
                "password": "test123",
                "port": 5432,
                "user": "nishant",
            },
        }
    },
    "apps": {
        "main": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
