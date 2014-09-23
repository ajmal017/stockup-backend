#!/bin/bash

# mount disk
sudo fdisk -l
echo -n "What is the name of the disk? "
read diskName
echo "n                                                                                                            
p                                                                                                                  
1


w                                                                                                                  
" | sudo fdisk /dev/$diskName

sudo mkfs -t ext4 /dev/"$diskName"1
sudo mkdir /data-drive
sudo mount /dev/"$diskName"1 /data-drive
sudo chown trader:trader /data-drive
line=$(sudo -i blkid|tail -1)
words=($line)
UUID=${line[1]}
sudo echo "$UUID /data-drive ext4 defaults 1 2" >> /etc/fstab

#generate ssh key
cd ~/.ssh
ssh-keygen -t rsa -C "robert.guo@10gen.com" -f id_rsa -N ''
echo "please add this key to github ,press [Enter] when done"
more id_rsa.pub
read placeholder

aptInstall () {
	echo "Y" | sudo apt-get install $1 &> ~/init-script.log
}

echo "Installing things, may take a while..."
aptInstall apache2
aptInstall php5
aptInstall nodejs
aptInstall nodejs-legacy
aptInstall npm
aptInstall mongodb
aptInstall git
aptInstall emacs
aptInstall python-dev
aptInstall python-pip
aptInstall libcurl4-openssl-dev

sudo pip install pymongo
sudo pip install supervisor

# shorthands
addAbbrev () {
    echo $1 >> ~/.bash_profile
}

upgate() {
	sudo apt-get update
	echo "Y" | sudo apt-get upgrade &> ~/init-script.log
}

# git stuff
addAbbrev "alias gclone='git clone git@github.com:guoyr/stockup-backend.git'"
addAbbrev "alias ls='ls -G'"
addAbbrev "gcam() {git commit -am \"$1\"}"
addAbbrev "alias sctl=sudo supervisorctl -c '/var/www/stockup-backend/deployment/supervisord.conf'"
addAbbrev "export PYTHONPATH=$PYTHOPATH:/var/www/stockup-backend/"

git config --global user.name "Robert Guo"
git config --global user.email "robert.guo@10gen.com"

# setup deployment hook

sudo mkdir /var/www/.ssh
sudo chown -R www-data:www-data /var/www/.ssh/

sudo cp ~/.ssh/id_rsa.pub /var/www/.ssh/
sudo cp ~/.ssh/id_rsa /var/www/.ssh/

sudo chown -R www-data:www-data /var/www/

sudo -Hu www-data git clone git@github.com:guoyr/stockup-backend.git /var/www/stockup-backend
sudo -Hu www-data ln -s /var/www/stockup-backend/deployment/deploy.php /var/www/html/deploy.php
cd /var/www/stockup-backend/servers
sudo pip install -r requirements.txt
# sudo npm isntall nodemon
# npm install

sudo cp /var/www/stockup-backend/deployment/000-default.conf /etc/apache2/sites-enabled/000-default.conf
sudo cp /var/www/stockup-backend/deployment/ports.conf /etc/apache2/ports.conf 
sudo cp /var/www/stockup-backend/deployment/mongodb.conf /etc/init/mongodb.conf

# start MongoDB
mkdir /data-drive/db/
mkdir /data-drive/log/	

# TODO: change to use replica set and config file
(echo "@reboot  sudo /usr/local/bin/mongod --dbpath /data-drive/db/ --logpath /data-drive/log/mongodb.log --fork")| sudo crontab -
(crontab -l ; echo "@reboot sudo supervisord -c /var/www/stockup-backend/deployment/supervisord.conf")| sudo crontab -
(crontab -l ; echo "* 1,4,8 * * * sudo supervisorctl -c '/var/www/stockup-backend/deployment/supervisord.conf' restart data_server1 data_server2 data_server3 data_server4")| sudo crontab -


