#!/bin/bash
cd ~
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
echo "$UUID /data-drive ext4 defaults 1 2" >> /etc/fstab

#generate ssh key
cd ~/.ssh
ssh-keygen -t rsa -C "robert.guo@10gen.com" -f id_rsa -N ''
echo "please add this key to github ,press [Enter] when done"
echo id_rsa
read placeholder

cd /
sudo apt-get update
echo "Y" | sudo apt-get upgrade

echo "Y" | sudo apt-get install apache2
echo "Y" | sudo apt-get install php5
echo "Y" | sudo apt-get install nodejs
echo "Y" | sudo apt-get install mongodb
echo "Y" | sudo apt-get install git
echo "Y" | sudo apt-get install emacs

echo "alias gclone='git clone git@github.com:guoyr/stockup-backend.git'" >> ~/.bashrc

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


# start MongoDB
mkdir /data-drive/db/
mkdir /data-drive/log/	
(crontab -l ; echo "@reboot sudo /usr/bin/mongod --dbpath /data-drive/db/ --logpath /data-drive/log/mongodb.log")| crontab -

