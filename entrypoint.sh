#! /bin/sh

if $INITIALIZE_DB = true; then
    echo "Initializing Database"
    aerich init -t tortoise_config.tortoise_config
    aerich init-db
fi

if $MIGRATE_DB = true; then
    echo "Migrating Database"
    aerich migrate
    aerich upgrade

fi


sleep 5s
python -m itsnp