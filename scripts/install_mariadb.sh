#!/bin/bash
sudo apt-get install mariadb-server
sudo service mysql stop
sudo mysql_install_db
sudo service mysql start
sudo mysql_secure_installation
sudo apt-get install mariadb-plugin-tokudb
