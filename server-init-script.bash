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
echo id_rsa
read placeholder

aptInstall () {
	echo "Y" | sudo apt-get install $1 &> ~/init-script.log
}

echo "Installing things, may take a while..."
aptInstall apache2
aptInstall php5
aptInstall nodejs
aptInstall npm
aptInstall mongodb
aptInstall git
aptInstall emacs
aptInstall python-dev
aptInstall python-pip
sudo pip install pymongo

# shorthands
addAbbrev () {
	echo $1 >> ~/.bash_profile
}

upgate() {
	sudo apt-get update
	echo "Y" | sudo apt-get upgrade &> ~/init-script.log
}

addAbbrev "alias gclone='git clone git@github.com:guoyr/stockup-backend.git'"
addAbbrev "alias ls='ls -G'"


git config --global user.name "Robert Guo"
git config --global user.email "robert.guo@10gen.com"

# setup deployment hook
sudo mkdir /var/www/.ssh
sudo chown -R www-data:www-data /var/www/.ssh/

sudo cp ~/.ssh/id_rsa.pub /var/www/.ssh/
sudo cp ~/.ssh/id_rsa /var/www/.ssh/

sudo chown -R www-data:www-data /var/www/

sudo -Hu www-data git clone git@github.com:guoyr/stockup-backend.git /var/www/stockup-backend
sudo -Hu www-data ln -s /var/www/stockup-backend/deploy.php /var/www/html/deploy.php
cd /var/www/stockup-backend
npm install

# start MongoDB
mkdir /data-drive/db/
mkdir /data-drive/log/	
(crontab -l ; echo "@reboot sudo /usr/bin/mongod --dbpath /data-drive/db/ --logpath /data-drive/log/mongodb.log")| crontab -




