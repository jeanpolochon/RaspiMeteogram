#!/bin/bash

if [ "$(whoami)" != "root" ]; then
	echo "Please execute this script as a root"
	exit 1
fi
mkdir -p ./log
touch ./log/log_install.txt

echo "Installing the required packages"
echo "Installing apache web server"
apt-get install apache2 -y >>./log/log_install.txt
echo "Installing PHP"
apt-get install php -y  >>./log/log_install.txt
echo "Installing MySQL"
apt-get install mysql-server python-mysqldb php-mysql python.connector -y  >>./log/log_install.txt

echo "Installing packages for the i2c connection"
apt-get install i2c-tools python-smbus -y >>./log/log_install.txt

echo "Restarting Apache webserver"
service apache2 restart

echo "Setting up the database"
# create random password
PASSWDDB="$(openssl rand -base64 12)"

# replace "-" with "_" for database username
if [ $SUDO_USER ]; then user=$SUDO_USER; else user=`whoami`; fi
MAINDB=${user//[^a-zA-Z0-9]/_}
echo "Mysql user will be '$MAINDB' and database name will be '$MAINDB'"

mysql --execute "CREATE DATABASE IF NOT EXISTS ${MAINDB};" >>./log/log_install.txt
mysql --execute "CREATE USER IF NOT EXISTS ${MAINDB}@localhost IDENTIFIED BY '${PASSWDDB}';" >>./log/log_install.txt
mysql --execute "GRANT ALL PRIVILEGES ON ${MAINDB}.* TO '${MAINDB}'@'localhost';" >>./log/log_install.txt
mysql --execute "FLUSH PRIVILEGES;" >>./log/log_install.txt

mysql --execute "CREATE TABLE IF NOT EXISTS ${MAINDB}.records(tdatetime DATETIME, temperature DECIMAL(4,1), pressure DECIMAL(5,1), humidity DECIMAL(4,1));" >>./log/log_install.txt

echo [db-meteogram]>db.conf
echo username=${MAINDB}>>db.conf
echo password=${PASSWDDB}>>db.conf
echo database=${MAINDB}>>db.conf
echo table=records>>db.conf
echo "Database is set up"

echo "Setting up cron job"
(sudo crontab -l ; echo "*/1 * * * * /usr/bin/python /home/pi/RaspiMeteogram/acquire.py > /var/log/meteogram.log 2>&1") | sort - | uniq - | sudo crontab -
echo "Install complete"
