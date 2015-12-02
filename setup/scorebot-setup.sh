#!/bin/bash
# This script will install scorebot on ubuntu systems
# note: This has only been tested on ubuntu but may work on debian as well
#
# If your doing development on scorebot, you may wish to checkout gi0cann's
# vagrant installer/setup on github https://github.com/gionnec/scorebot-vagrant

RED='\033[00;31m'
YELLOW='\033[00;33m'
BLUE='\033[00;34m'
WHITE='\033[01;37m'
ORG='\033[0m'

if [ "$EUID" -ne 0 ]
	then printf "${RED}This script needs to be run as root${ORG}\n"
	exit 1
fi

if dpkg --list mysql-server | egrep -q ^ii; then
	printf "${YELLOW}Mysql is already installed, you will need to provide the root password:${ORG}"
	read sqlpass
		while ! mysql -u root -p$sqlpass -e ";" ; do
                printf "${YELLOW}Cannot connect, please retry:${ORG} "
		read sqlpass
                done
else
	printf "${YELLOW}This setup script will install MySQLd. Please provide a password for the 'root' user:${ORG} "
	read newsqlpass
	printf "${YELLOW}Confirm: ${ORG}"
	read newsqlpass2
		while [ $newsqlpass != $newsqlpass2 ]; do
		printf "${YELLOW}Passwords did not match, Please try agian:${ORG} "
		read newsqlpass
        	printf "${YELLOW}Confirm: ${ORG}"
		read newsqlpass2
		done
	debconf-set-selections <<< "mysql-server mysql-server/root_password password $newsqlpass"
	debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $newsqlpass"
	sqlpass=$newsqlpass
fi
printf "${YELLOW}We need to add a 'scorebot' user to MySQL. Please provide a password:${ORG} "
read scorepass
printf "${YELLOW}Confirm:${ORG} "
read scorepass2
while [ $scorepass != $scorepass2 ]; do
printf "${YELLOW}Password MisMatch, Try again:${ORG} "
read scorepass
printf "${YELLOW}Confirm:${ORG} "
read scorepass2
done


printf "\n${YELLOW}### Checking if the system needs updates ### ${ORG}\n\n"
apt-get update && apt-get upgrade -y
printf "\n${YELLOW}###         Installing Dependencies      ###\n"
printf "### This could take awhile, grab a beer! ###${ORG}\n\n"
apt-get install -y python-dnspython python-rrdtool apache2 php5 php5-mysql python-pymongo python-dns python-mysqldb git mongodb mysql-server mysql-client python-pip build-essential python-dev libav-tools
printf "\n${YELLOW}### Installing required python libraries ### ${ORG}\n\n"
pip install jaraco.modb bottle paste requests backports.functools_lru_cache
printf "\n${YELLOW}### Ensuring all installed python libraries are up2date ### ${ORG}\n\n"
python pip-update.py
printf "\n${YELLOW}### Coping Ticket System to /var/www/html ###${ORG}\n\n"
cp -rf sts/ /var/www/html

printf "\n${YELLOW}### CREATING Ticket DATABASE and scorebot user ###${ORG}\n\n"
mysql --user="root" --password="$sqlpass" --execute="CREATE DATABASE sts; GRANT ALL ON sts.* TO scorebot@'localhost' IDENTIFIED BY '$scorepass';"

printf "${YELLOW}### Adding Tables to Ticket System ###${ORG}\n\n"
mysql --user="scorebot" --password="$scorepass" sts < sts/config/sts.sql

# Add groups
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.groups (id ,name)VALUES (NULL , 'ALPHA');"
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.groups (id ,name)VALUES (NULL , 'BRAVO');"
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.groups (id ,name)VALUES (NULL , 'CHARLIE');"
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.groups (id ,name)VALUES (NULL , 'DELTA');"
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.groups (id ,name)VALUES (NULL , 'GAMMA');"

#Add Locations
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.locations (id ,name ,address ,type)VALUES (NULL , 'alpha.net', '', '1');"
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.locations (id ,name ,address ,type)VALUES (NULL , 'bravo.net', '', '1');"
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.locations (id ,name ,address ,type)VALUES (NULL , 'charlie.net', '', '1');"
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.locations (id ,name ,address ,type)VALUES (NULL , 'delta.net', '', '1');"
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.locations (id ,name ,address ,type)VALUES (NULL , 'gamma.net', '', '1');"

# Add Users
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.users (id ,fn ,ln ,mail ,password ,acl_id ,location_id ,group_id ,fpc ,state ,login_attempts ,last_login_ip ,last_login_dt ,profile_pic_path)VALUES (NULL , 'ALPHA', 'ALPHA', 'alpha@alpha.net', '', '2', '1', '1', '1', '0', '0', '0', '0', '');"
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.users (id ,fn ,ln ,mail ,password ,acl_id ,location_id ,group_id ,fpc ,state ,login_attempts ,last_login_ip ,last_login_dt ,profile_pic_path)VALUES (NULL , 'BRAVO', 'BRAVO', 'bravo@bravo.net', '', '2', '2', '2', '1', '0', '0', '0', '0', '');"
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.users (id ,fn ,ln ,mail ,password ,acl_id ,location_id ,group_id ,fpc ,state ,login_attempts ,last_login_ip ,last_login_dt ,profile_pic_path)VALUES (NULL , 'CHARLIE', 'CHARLIE', 'charlie@charlie.net', '', '2', '3', '3', '1', '0', '0', '0', '0', '');"
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.users (id ,fn ,ln ,mail ,password ,acl_id ,location_id ,group_id ,fpc ,state ,login_attempts ,last_login_ip ,last_login_dt ,profile_pic_path)VALUES (NULL , 'DELTA', 'DELTA', 'delta@delta.net', '', '2', '4', '4', '1', '0', '0', '0', '0', '');"
mysql -uscorebot -p$scorepass --execute="INSERT INTO sts.users (id ,fn ,ln ,mail ,password ,acl_id ,location_id ,group_id ,fpc ,state ,login_attempts ,last_login_ip ,last_login_dt ,profile_pic_path)VALUES (NULL , 'GAMMA', 'GAMMA', 'gamma@gama.net', '', '2', '5', '5', '1', '0', '0', '0', '0', '');"

printf "${YELLOW}###############################################################\n"
printf "#                                                             #\n"
printf "#                   Installation Complete!                    #\n"
printf "# ${RED}Please review docs/index.html  on how to configure scorebot${YELLOW} #\n"
printf "#                                                             #\n"
printf "           ${BLUE}MySQLd root password = ${RED}$sqlpass${YELLOW}\n"
printf "           ${BLUE}scorebot sql password = ${RED}$scorepass${YELLOW}\n"
printf "###############################################################${ORG}\n"
