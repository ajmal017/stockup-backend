#generate ssh key
cd ~/.ssh
ssh-keygen -t rsa -C "robert.guo@10gen.com" -f id_rsa -N ''
echo "please add this key to github"
echo id_rsa

sudo apt-get update
echo "Y" | sudo apt-get upgrade

echo "Y" | sudo apt-get install apache2
echo "Y" | sudo apt-get install php5
echo "Y" | sudo apt-get install nodejs
echo "Y" | sudo apt-get install emacs

echo "Y" | sudo apt-get install git

echo "alias gclone='git clone git@github.com:guoyr/stockup-backend.git'" >> ~/.bashrc

git config --global user.name "Robert Guo"
git config --global user.email "robert.guo@10gen.com"

sudo mkdir /var/www/.ssh
sudo chown -R www-data:www-data /var/www/.ssh/

sudo cp ~/.ssh/id_rsa.pub /var/www/.ssh/
sudo cp ~/.ssh/id_rsa /var/www/.ssh/

sudo chown -R www-data:www-data /var/www/

sudo -Hu www-data git clone git@github.com:guoyr/stockup-backend.git /var/www/stockup-backend

