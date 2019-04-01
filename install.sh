#!/bin/bash

echo "Setting up the database.."
# create random password
PASSWDDB="$(openssl rand -base64 12)"

# replace "-" with "_" for database username
if [ $SUDO_USER ]; then user=$SUDO_USER; else user=`whoami`; fi
MAINDB=${user//[^a-zA-Z0-9]/_}
echo "Mysql user will be $MAINDB and database name will be $MAINDB"

mysql --execute "CREATE DATABASE ${MAINDB};"
mysql --execute "CREATE USER ${MAINDB}@localhost IDENTIFIED BY '${PASSWDDB}';"
mysql --execute "GRANT ALL PRIVILEGES ON ${MAINDB}.* TO '${MAINDB}'@'localhost';"
mysql --execute "FLUSH PRIVILEGES;"

mysql --execute "CREATE TABLE ${MAINDB}.records(tdate DATE, ttime TIME, temperature DECIMAL(4,1), pressure DECIMAL(5,1), humidity DECIMAL(4,1));"

echo "Database is set up"
