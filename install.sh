#!/bin/bash

if [ "$(whoami)" != "root" ]; then
	echo "Please execute this script as a root"
	exit 1
fi
mkdir -p ./log
touch ./log/log\install.txt

echo "Making sure that the OS is up to date"
apt-get update >>./log/log\install.txt
apt-get upgrade >>./log/log\install.txt

echo "Installing the required packages"
echo "Installing apache web server"
apt-get install apache2 -y >>./log/log\install.txt
echo "Installing PHP"
apt-get install php -y  >>./log/log\install.txt
echo "Installing MySQL"
apt-get install mysql-server python-mysqldb php-mysql -y  >>./log/log\install.txt

echo "Restarting Apache webserver"
service apache2 restart

echo "Setting up the database"
# create random password
PASSWDDB="$(openssl rand -base64 12)"

# replace "-" with "_" for database username
if [ $SUDO_USER ]; then user=$SUDO_USER; else user=`whoami`; fi
MAINDB=${user//[^a-zA-Z0-9]/_}
echo "Mysql user will be '$MAINDB' and database name will be '$MAINDB'"

mysql --execute "CREATE DATABASE ${MAINDB};" >>./log/log\install.txt
mysql --execute "CREATE USER ${MAINDB}@localhost IDENTIFIED BY '${PASSWDDB}';" >>./log/log\install.txt
mysql --execute "GRANT ALL PRIVILEGES ON ${MAINDB}.* TO '${MAINDB}'@'localhost';" >>./log/log\install.txt
mysql --execute "FLUSH PRIVILEGES;" >>./log/log\install.txt

mysql --execute "CREATE TABLE ${MAINDB}.records(tdate DATE, ttime TIME, temperature DECIMAL(4,1), pressure DECIMAL(5,1), humidity DECIMAL(4,1));" >>./log/log\install.txt

echo "Database is set up"
